from pydantic import BaseModel, Field
from apps.schemas.embedding import EmbeddingModel


class ClusterModel(BaseModel):
    cluster_center: list[float] = Field(..., description="聚类中心坐标")
    embeddings: list[EmbeddingModel] = Field(..., description="属于该簇的嵌入向量列表")


class ClustersModel(BaseModel):
    clusters: list[ClusterModel] = Field(..., description="聚类结果列表")
    outliers: list[EmbeddingModel] = Field(..., description="离群点嵌入向量列表")
