from datetime import datetime
from uuid import uuid4

from ENUM.exprience import ExperienceStatus, ExperienceType
from pydantic import BaseModel, Field


class Experience(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: ExperienceType = Field(default=ExperienceType.WIKI)
    name: str = Field(default="")
    description: str = Field(default="")
    keywords: list[str] = Field(default_factory=list)
    references: str = Field(default="")  # JSON 字符串，来自 YAML front matter 的 references
    status: ExperienceStatus = Field(default=ExperienceStatus.EXISTED)
    is_hot: int = Field(default=0)
    source: str = Field(default="")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
