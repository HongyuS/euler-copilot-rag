from apps.schemas.embedding import EmbeddingModel
from apps.schemas.cluster import ClusterModel, ClustersModel


class ClusterService:
    @staticmethod
    async def DBSCAN(
        batch_size: int,
        # 离群点数量
        outlier_threshold: int,
        # 距离
        eps: float,
        # 最小样本数
        min_samples: int,
        embeddings: list[EmbeddingModel]
    ) -> ClustersModel:
        """
        DBSCAN聚类服务
        层次化识别离群点，每次将要聚类的特征分为k条一个batch进行聚类，提取离群点，对于提取的离群点的数量小于阈值
        则将这些离群点加入到下一个batch中继续进行聚类，直到所有特征都被处理完毕
        这样做的目的是为了减少内存占用，防止一次性将所有特征进行聚类导致内存溢出
        但这样做的缺点是可能会导致离群点识别不够准确
        """
        pass

    @staticmethod
    async def KMeans(
        batch_size: int,
        # 聚类数量
        n_clusters: int,
        # 迭代次数
        n_init: int,
        # 随机种子
        random_state: int,
        embeddings: list[EmbeddingModel]
    ) -> ClustersModel:
        """
        KMeans聚类服务
        层次化聚类，每次将要聚类的特征分为k条一个batch进行聚类，最后将所有batch的聚类结果再进行一次聚类直到所有聚类结果合并为止
        这样做的目的是为了减少内存占用，防止一次性将所有特征进行聚类导致内存溢出
        但这样做的缺点是可能会导致聚类结果不够准确
        """
        pass
