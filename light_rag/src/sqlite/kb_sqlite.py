"""
知识库数据库 - kb.db ORM 模型和连接池
"""
from sqlalchemy import (
    Column, String, Integer, Text, DateTime, ForeignKey, 
    LargeBinary, Index, func, create_engine, text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from datetime import datetime
import os
import logging
import threading

from common.config import get_embedding_vector_dimension
import sqlite_vec

logger = logging.getLogger(__name__)

Base = declarative_base()


class KnowledgeBase(Base):
    """知识库表"""
    __tablename__ = 'knowledge_bases'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    chunk_size = Column(Integer, nullable=False)
    embedding_model = Column(Text)
    embedding_endpoint = Column(Text)
    embedding_api_key = Column(Text)
    status = Column(String, default='excited', nullable=False)  # 'excited' 或 'deleted'
    created_at = Column(DateTime, default=datetime.now, server_default=func.current_timestamp())
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, server_default=func.current_timestamp())
    
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_kb_name', 'name'),
    )


class Document(Base):
    """文档表"""
    __tablename__ = 'documents'
    
    id = Column(String, primary_key=True)
    kb_id = Column(String, ForeignKey('knowledge_bases.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    file_path = Column(Text)
    file_type = Column(String)
    content = Column(Text)  # 文档完整内容
    chunk_size = Column(Integer)
    status = Column(String, default='excited', nullable=False)  # 'excited' 或 'deleted'
    created_at = Column(DateTime, default=datetime.now, server_default=func.current_timestamp())
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, server_default=func.current_timestamp())
    
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_doc_kb_id', 'kb_id'),
        Index('idx_doc_name', 'name'),
    )


class Chunk(Base):
    """文档分块表"""
    __tablename__ = 'chunks'
    
    id = Column(String, primary_key=True)
    doc_id = Column(String, ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    tokens = Column(Integer)
    chunk_index = Column(Integer)
    embedding = Column(LargeBinary)  # 向量嵌入
    created_at = Column(DateTime, default=datetime.now, server_default=func.current_timestamp())
    
    document = relationship("Document", back_populates="chunks")
    
    __table_args__ = (
        Index('idx_chunk_doc_id', 'doc_id'),
        Index('idx_chunk_index', 'chunk_index'),
    )


class DatabaseConnectionManager:
    """数据库连接管理器（单例模式）"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._engines = {}
        self._session_factories = {}
        self._initialized = True
    
    def init_database(self, db_path: str):
        """
        初始化数据库连接池
        :param db_path: 数据库文件路径
        """
        abs_db_path = os.path.abspath(db_path)
        if abs_db_path in self._engines:
            return
        db_dir = os.path.dirname(abs_db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        engine = create_engine(
            f'sqlite:///{abs_db_path}',
            echo=False,
            connect_args={'check_same_thread': False}
        )
        session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        self._engines[abs_db_path] = engine
        self._session_factories[abs_db_path] = session_factory
        self._init_database_tables(engine)
    
    def _init_database_tables(self, engine):
        """初始化数据库表结构"""
        try:
            Base.metadata.create_all(engine)
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                        id UNINDEXED,
                        content,
                        content_rowid=id
                    )
                """))
                try:
                    raw_conn = conn.connection.dbapi_connection
                    raw_conn.enable_load_extension(True)
                    sqlite_vec.load(raw_conn)
                    raw_conn.enable_load_extension(False)
                except Exception as e:
                    logger.warning(f"加载 sqlite-vec 扩展失败: {e}")
                try:
                    vector_dim = get_embedding_vector_dimension()
                    conn.execute(text(f"""
                        CREATE VIRTUAL TABLE IF NOT EXISTS vec_index USING vec0(
                            embedding float[{vector_dim}]
                        )
                    """))
                except Exception as e:
                    logger.warning(f"创建 vec_index 表失败: {e}")
        except Exception as e:
            logger.exception(f"[kb_sqlite] 初始化数据库失败: {e}")
            raise e
    
    def get_engine(self, db_path: str = None):
        if db_path is None:
            if not self._engines:
                raise RuntimeError("数据库引擎未初始化，请先调用 init_database()")
            return next(iter(self._engines.values()))
        abs_db_path = os.path.abspath(db_path)
        if abs_db_path not in self._engines:
            raise RuntimeError(f"数据库引擎未初始化，请先调用 init_database('{db_path}')")
        return self._engines[abs_db_path]
    
    def get_session(self, db_path: str = None) -> Session:
        if db_path is None:
            if not self._session_factories:
                raise RuntimeError("数据库会话工厂未初始化，请先调用 init_database()")
            return next(iter(self._session_factories.values()))()
        abs_db_path = os.path.abspath(db_path)
        if abs_db_path not in self._session_factories:
            raise RuntimeError(f"数据库会话工厂未初始化，请先调用 init_database('{db_path}')")
        return self._session_factories[abs_db_path]()


_db_manager = DatabaseConnectionManager()


def init_database(db_path: str):
    """初始化数据库连接池"""
    return _db_manager.init_database(db_path)


def get_engine(db_path: str = None):
    """获取数据库引擎"""
    return _db_manager.get_engine(db_path)


def get_session(db_path: str = None) -> Session:
    """获取数据库会话"""
    return _db_manager.get_session(db_path)
