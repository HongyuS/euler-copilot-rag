"""
Chunk 检索管理模块 - 包含关键词检索和向量检索
"""
import logging
import struct
from typing import List, Dict, Any, Optional
from sqlalchemy import text
import jieba

logger = logging.getLogger(__name__)


class ChunkManager:
    """Chunk 检索管理类（静态方法）"""
    
    @staticmethod
    def _prepare_fts_query(query: str) -> str:
        """
        准备 FTS5 查询
        :param query: 原始查询文本
        :return: FTS5 查询字符串
        """
        def escape_fts_word(word: str) -> str:
            # 包含以下任意字符时，整体作为短语用双引号包裹，避免触发 FTS5 语法解析
            special_chars = [
                '"', "'", '(', ')', '*', ':', '?', '+', '-', '|', '&',
                '{', '}', '[', ']', '^', '$', '\\', '/', '!', '~', ';',
                ',', '.', ' ', '%'
            ]
            if any(char in word for char in special_chars):
                escaped_word = word.replace('"', '""')
                return f'"{escaped_word}"'
            return word
        
        try:
            words = jieba.cut(query)
            words = [word.strip() for word in words if word.strip()]
            if not words:
                return escape_fts_word(query)
            
            escaped_words = [escape_fts_word(word) for word in words]
            fts_query = ' OR '.join(escaped_words)
            return fts_query
        except Exception:
            return escape_fts_word(query)
    
    @staticmethod
    def search_by_keyword(conn, query: str, top_k: int = 5, doc_ids: Optional[List[str]] = None, banned_chunk_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        关键词检索（FTS5，使用 jieba 对中文进行分词）
        :param conn: 数据库连接对象（SQLAlchemy Connection）
        :param query: 查询文本
        :param top_k: 返回数量
        :param doc_ids: 可选的文档ID列表，用于过滤
        :param banned_chunk_ids: 可选的被禁用的chunk ID列表，用于过滤
        :return: chunk 列表
        """
        try:
            fts_query = ChunkManager._prepare_fts_query(query)
            
            params = {"fts_query": fts_query, "top_k": top_k}
            where_clause = "WHERE chunks_fts MATCH :fts_query"
            
            if doc_ids:
                placeholders = ','.join([f':doc_id_{i}' for i in range(len(doc_ids))])
                for i, doc_id in enumerate(doc_ids):
                    params[f'doc_id_{i}'] = doc_id
                where_clause += f" AND c.doc_id IN ({placeholders})"
            
            if banned_chunk_ids:
                banned_placeholders = ','.join([f':banned_chunk_id_{i}' for i in range(len(banned_chunk_ids))])
                for i, banned_id in enumerate(banned_chunk_ids):
                    params[f'banned_chunk_id_{i}'] = banned_id
                where_clause += f" AND c.id NOT IN ({banned_placeholders})"
            
            sql = f"""
                SELECT c.id, c.doc_id, c.content, c.tokens, c.chunk_index,
                       d.name as doc_name,
                       chunks_fts.rank
                FROM chunks_fts
                JOIN chunks c ON c.id = chunks_fts.id
                JOIN documents d ON d.id = c.doc_id
                {where_clause}
                ORDER BY chunks_fts.rank
                LIMIT :top_k
            """
            result = conn.execute(text(sql), params)
            
            results = []
            for row in result:
                results.append({
                    'id': row.id,
                    'doc_id': row.doc_id,
                    'content': row.content,
                    'tokens': row.tokens,
                    'chunk_index': row.chunk_index,
                    'doc_name': row.doc_name,
                    'score': row.rank if row.rank is not None else 0.0
                })
            return results
        except Exception as e:
            logger.exception(f"[KeywordSearch] 关键词检索失败: {e}")
            return []
    
    @staticmethod
    def search_by_vector(conn, query_vector: List[float], top_k: int = 5, doc_ids: Optional[List[str]] = None, banned_chunk_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        向量检索
        :param conn: 数据库连接对象（SQLAlchemy Connection）
        :param query_vector: 查询向量
        :param top_k: 返回数量
        :param doc_ids: 可选的文档ID列表，用于过滤
        :param banned_chunk_ids: 可选的被禁用的chunk ID列表，用于过滤
        :return: chunk 列表
        """
        try:
            # 检查 vec_index 表是否存在
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='vec_index'
            """))
            if not result.fetchone():
                return []
            
            query_vector_bytes = struct.pack(f'{len(query_vector)}f', *query_vector)
            
            params = {"query_vector": query_vector_bytes, "top_k": top_k}
            where_clause = "WHERE v.embedding MATCH :query_vector AND k = :top_k"
            
            if doc_ids:
                placeholders = ','.join([f':doc_id_{i}' for i in range(len(doc_ids))])
                for i, doc_id in enumerate(doc_ids):
                    params[f'doc_id_{i}'] = doc_id
                where_clause += f" AND c.doc_id IN ({placeholders})"
            
            if banned_chunk_ids:
                banned_placeholders = ','.join([f':banned_chunk_id_{i}' for i in range(len(banned_chunk_ids))])
                for i, banned_id in enumerate(banned_chunk_ids):
                    params[f'banned_chunk_id_{i}'] = banned_id
                where_clause += f" AND c.id NOT IN ({banned_placeholders})"
            
            sql = f"""
                SELECT c.id, c.doc_id, c.content, c.tokens, c.chunk_index,
                       d.name as doc_name,
                       distance
                FROM vec_index v
                JOIN chunks c ON c.rowid = v.rowid
                JOIN documents d ON d.id = c.doc_id
                {where_clause}
                ORDER BY distance
            """
            result = conn.execute(text(sql), params)
            
            results = []
            for row in result:
                results.append({
                    'id': row.id,
                    'doc_id': row.doc_id,
                    'content': row.content,
                    'tokens': row.tokens,
                    'chunk_index': row.chunk_index,
                    'doc_name': row.doc_name,
                    'score': row.distance
                })
            return results
        except Exception as e:
            logger.exception(f"[VectorSearch] 向量检索失败: {e}")
            return []
