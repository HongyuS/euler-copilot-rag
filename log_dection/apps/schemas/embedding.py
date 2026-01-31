from pydantic import BaseModel, Field
import uuid


class EmbeddingModel(BaseModel):
    id: str = Field(default_factory=lambda: str(
        uuid.uuid4()), description="嵌入向量ID")
    vector: list[float] = Field(..., description="嵌入向量数据")
