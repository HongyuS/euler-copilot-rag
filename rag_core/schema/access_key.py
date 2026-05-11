from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field
from ENUM.general import ExistedStatus


class AccessKey(BaseModel):
    name: str = Field("", description="访问密钥名称")
    description: str = Field("", description="访问密钥描述")
    key: str = Field(default_factory=lambda: str(uuid4()), description="访问密钥")
    owner_id: str = Field(..., description="访问密钥所属用户ID")
    owner_name: str = Field(..., description="访问密钥所属用户名")
    existed_status: ExistedStatus = Field(
        ExistedStatus.EXISTED, description="访问密钥存在状态"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="访问密钥创建时间",
    )
