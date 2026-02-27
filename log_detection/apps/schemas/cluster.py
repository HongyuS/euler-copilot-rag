from pydantic import BaseModel, Field
from apps.schemas.log import LogTemplateModel


class ClusterModel(BaseModel):
    is_outlier: bool = Field(default=False, description="是否为离群点")
    cluster_center: list[float] = Field(..., description="聚类中心坐标")
    log_templates: list[LogTemplateModel] = Field(
        ..., description="聚类中的日志模板列表")
