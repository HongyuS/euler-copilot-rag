import logging
from rag_core.config.config import Config
from rag_core.database.base_class import BaseDataBase

logger = logging.getLogger(__name__)


class BaseVectorDataBase(BaseDataBase):
    """
    向量数据库操作抽象基类（虚类）
    定义通用逻辑，子类必须实现：获取数据库连接URL、初始化数据库特殊逻辑
    """

    # 类变量初始化

    def __init__(self) -> None:
        pass

    @staticmethod
    def init_database_specifics() -> None:
        """
        【抽象方法】子类必须实现：数据库专属初始化逻辑（如插件注册、连接监听等）
        """
        vector_db_config = Config().get_config().vector_db
        logger.info(f"正在初始化向量数据库，类型：{vector_db_config.database_type}")
        # 子类实现数据库专属初始化逻辑
        BaseVectorDataBase.find_sub_class(
            vector_db_config.database_type
        ).init_database_specifics(vector_db_config)

    @staticmethod
    async def get_session(cls) -> BaseDataBase._ConnectionManager:
        """通用：获取数据库会话（上下文管理器）"""
        session = BaseVectorDataBase.find_sub_class(
            Config().get_config().vector_db.database_type
        ).get_session(cls)
        return BaseDataBase._ConnectionManager(session)
