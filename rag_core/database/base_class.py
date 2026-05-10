from ENUM.database import ScaleDbType, VectorDbType, GraphDbType


class BaseDataBase:
    """
    向量数据库操作抽象基类（虚类）
    定义通用逻辑，子类必须实现：获取数据库连接URL、初始化数据库特殊逻辑
    """

    class _ConnectionManager:
        """通用：异步上下文管理器，管理数据库连接关闭"""

        def __init__(self, connection):
            self.connection = connection

        async def __aenter__(self):
            return self.connection

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            await self.connection.close()

    @staticmethod
    def find_sub_class(database_type: ScaleDbType | VectorDbType | GraphDbType):
        subclasses = BaseDataBase.__subclasses__()
        for subclass in subclasses:
            if database_type in subclass.name:
                return subclass
        return None
