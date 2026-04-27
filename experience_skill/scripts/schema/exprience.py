from ENUM.exprience import ExperienceType, ExperienceStatus
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime


class Experience(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: ExperienceType = Field(default=ExperienceType.WIKI)
    description: str = Field(default="")
    keywords: list[str] = Field(default_factory=list)
    status: ExperienceStatus = Field(default=ExperienceStatus.EXISTED)
    is_hot: int = Field(default=0)
    source: str = Field(default="")
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat("y-%m-%d %H:%M:%S")
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat("y-%m-%d %H:%M:%S")
    )
