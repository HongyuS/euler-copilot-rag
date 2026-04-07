"""
数据库操作类 - 使用 SQLAlchemy ORM
"""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError

from sqlite.kb_sqlite import (
    Base, KnowledgeBase, Document,
    init_database, get_engine, get_session
)
from manager.document_manager import DocumentManager

logger = logging.getLogger(__name__)


class Database:
    """SQLite 数据库操作类 - 使用 SQLAlchemy ORM"""
    
    def __init__(self, db_path: str = "knowledge_base.db"):
        """
        初始化数据库连接
        :param db_path: 数据库文件路径
        """
        self.db_path = os.path.abspath(db_path)
        # 初始化数据库连接池（如果尚未初始化）
        init_database(self.db_path)
    
    def get_session(self):
        """获取数据库会话"""
        return get_session(self.db_path)
    
    def get_connection(self):
        """
        获取原始数据库连接（用于特殊操作，如 FTS5 和 vec_index）
        注意：此方法保留以兼容现有代码，但推荐使用 get_session()
        返回一个上下文管理器，使用后会自动关闭
        """
        return get_engine(self.db_path).connect()
    
    def add_knowledge_base(self, kb: KnowledgeBase) -> bool:
        """添加知识库"""
        session = self.get_session()
        try:
            session.add(kb)
            session.commit()
            return True
        except SQLAlchemyError as e:
            logger.exception(f"[Database] 添加知识库失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_knowledge_base(self, kb_name: str) -> Optional[KnowledgeBase]:
        """获取知识库（只返回excited状态）"""
        session = self.get_session()
        try:
            return session.query(KnowledgeBase).filter_by(name=kb_name, status='excited').first()
        finally:
            session.close()
    
    def delete_knowledge_bases_batch(self, kb_ids: List[str]) -> int:
        """批量软删除知识库（每批最多1024个）"""
        batch_size = 1024
        total_deleted = 0
        
        for i in range(0, len(kb_ids), batch_size):
            batch = kb_ids[i:i + batch_size]
            session = self.get_session()
            try:
                kbs = session.query(KnowledgeBase).filter(
                    KnowledgeBase.id.in_(batch),
                    KnowledgeBase.status == 'excited'
                ).all()
                
                for kb in kbs:
                    # 为每个知识库生成唯一的删除名称
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    base_new_name = f"{kb.name}_deleted_{timestamp}"
                    
                    # 检查新名称是否已存在（查询所有状态）
                    counter = 1
                    final_name = base_new_name
                    while session.query(KnowledgeBase).filter_by(name=final_name).first():
                        final_name = f"{kb.name}_deleted_{timestamp}_{counter}"
                        counter += 1
                    
                    # 更新名称和状态
                    kb.name = final_name
                    kb.status = 'deleted'
                    kb.updated_at = datetime.now()
                
                session.commit()
                total_deleted += len(kbs)
            except SQLAlchemyError as e:
                logger.exception(f"[Database] 批量删除知识库失败: {e}")
                session.rollback()
            finally:
                session.close()
        
        return total_deleted
    
    def list_knowledge_bases(self, keyword: Optional[str] = None) -> List[KnowledgeBase]:
        """列出所有知识库（只显示excited状态，支持关键词过滤）"""
        session = self.get_session()
        try:
            query = session.query(KnowledgeBase).filter(KnowledgeBase.status == 'excited')
            if keyword:
                query = query.filter(KnowledgeBase.name.ilike(f'%{keyword}%'))
            return query.order_by(KnowledgeBase.created_at.desc()).all()
        finally:
            session.close()


def get_kb_id_by_name(db: Database, kb_name: str, result: Dict[str, Any]) -> Optional[str]:
    """
    通过知识库名称获取知识库ID
    
    :param db: 数据库实例
    :param kb_name: 知识库名称
    :param result: 结果字典，用于设置错误消息
    :return: 知识库ID，如果不存在则返回None
    """
    try:
        kb = db.get_knowledge_base(kb_name)
        if not kb:
            result["message"] = f"知识库 '{kb_name}' 不存在"
            return None
        return kb.id
    except Exception as e:
        logger.exception(f"[get_kb_id_by_name] 获取知识库ID失败: {e}")
        result["message"] = f"获取知识库ID失败: {str(e)}"
        return None


def get_kb_ids_by_names(db: Database, kb_names: List[str], result: Dict[str, Any]) -> Optional[List[str]]:
    """
    通过知识库名称列表获取知识库ID列表
    
    :param db: 数据库实例
    :param kb_names: 知识库名称列表
    :param result: 结果字典，用于设置错误消息
    :return: 知识库ID列表，如果有知识库不存在则返回None
    """
    try:
        kb_ids = []
        for kb_name in kb_names:
            kb = db.get_knowledge_base(kb_name)
            if not kb:
                result["message"] = f"知识库 '{kb_name}' 不存在"
                return None
            kb_ids.append(kb.id)
        return kb_ids
    except Exception as e:
        logger.exception(f"[get_kb_ids_by_names] 获取知识库ID列表失败: {e}")
        result["message"] = f"获取知识库ID列表失败: {str(e)}"
        return None

