import logging
from rag_core.config.config import Config
from rag_core.database.base_class import BaseDataBase

logger = logging.getLogger(__name__)


class BaseVectorDataBase(BaseDataBase):
    """
    向量数据库操作抽象基类（虚类）
    定义通用逻辑，子类必须实现：获取数据库连接URL、初始化数据库特殊逻辑
    """

    # 类变量
    chunk_manager = None
    doc_manager = None
    json_manager = None
    convertor = None

    def __init__(self) -> None:
        pass

    @classmethod
    async def init_database_specifics(cls) -> None:
        """
        初始化向量数据库全局管理器（只执行一次）
        """
        # 1. 只查一次子类
        db_sub_class = BaseDataBase.find_sub_class(
            Config().get_config().vector_db.database_type
        )

        # 2. 赋值给当前类变量
        cls.chunk_manager = db_sub_class.chunk_manager
        cls.doc_manager = db_sub_class.doc_manager
        cls.json_manager = db_sub_class.json_manager
        cls.convertor = db_sub_class.convertor

        # 3. 日志
        vector_db_config = Config().get_config().vector_db
        logger.info(f"正在初始化向量数据库，类型：{vector_db_config.database_type}")

        # 4. 调用子类初始化（建表）
        await db_sub_class.init_database_specifics()

    @classmethod
    async def get_session(cls) -> BaseDataBase._ConnectionManager:
        """通用：获取数据库会话（上下文管理器）"""
        # 找到子类
        db_sub_class = BaseDataBase.find_sub_class(
            Config().get_config().vector_db.database_type
        )

        # 调用子类的 get_session
        return await db_sub_class.get_session()
