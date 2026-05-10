from pydantic import BaseModel, Field
from uuid import uuid4
from ENUM.general import OnlineStatus, LogLevel
from ENUM.model import ModelLabel, ModelProvider


class ServiceConfig(BaseModel):
    is_debug: bool = Field(default=False, description="是否启用调试模式")
    uvicorn_ip: str = Field(None, description="FastAPI 服务的IP地址")
    uvicorn_port: int = Field(None, description="FastAPI 服务的端口号")
    ssl_certfile: str = Field(None, description="SSL证书文件的路径")
    ssl_keyfile: str = Field(None, description="SSL密钥文件的路径")
    ssl_enable: bool = Field(None, description="是否启用SSL连接")
    log_level: LogLevel = Field(LogLevel.INFO, description="日志级别")


class DatabaseConfig(BaseModel):
    database_type: str = Field(default="postgres", description="数据库类型")
    database_host: str = Field(None, description="数据库地址")
    database_port: int = Field(None, description="数据库端口")
    database_user: str = Field(None, description="数据库用户名")
    database_password: str = Field(None, description="数据库密码")
    database_db: str = Field(None, description="数据库名称")
    # 连接池大小
    database_pool_size: int = Field(default=10, description="数据库连接池大小")


class TaskConfig(BaseModel):
    task_retry_time: int = Field(None, description="任务重试次数")
    cpu_limit: int = Field(default=64, description="任务使用CPU核数")


class ModelConfig(BaseModel):
    model_id: str | None = Field(
        default_factory=lambda: str(uuid4()), description="模型ID"
    )
    model_name: str = Field(None, description="模型名称")
    online_status: OnlineStatus = Field(OnlineStatus.ONLINE, description="模型在线状态")
    model_label: list[ModelLabel] = Field([], description="模型标签")
    model_provider: ModelProvider = Field(ModelProvider.OTHER, description="模型提供商")
    end_point: str = Field(None, description="模型服务接口地址")
    api_key: str = Field(None, description="模型服务API key")
    request_timeout: int = Field(default=60, description="请求超时时间")
    intput_max_tokens: int = Field(None, description="输入最大token数")
    output_max_tokens: int = Field(None, description="输出最大token数")
    temperature: float = Field(default=0.7, description="温度系数")


class DictBaseModel(BaseModel):
    def __getitem__(self, key):
        if key in self.__dict__:
            return getattr(self, key)
        return None


class ConfigModel(DictBaseModel):
    service: ServiceConfig = Field(..., description="服务配置")
    scalar_db: DatabaseConfig = Field(..., description="标量数据库配置")
    vector_db: DatabaseConfig = Field(..., description="向量数据库配置")
    graph_db: DatabaseConfig | None = Field(..., description="图数据库配置")
    task: TaskConfig = Field(..., description="任务配置")
    chat_model: ModelConfig = Field(..., description="聊天模型配置")
    embedding_model: ModelConfig | None = Field(..., description="文本嵌入模型配置")
    rerank_model: ModelConfig | None = Field(..., description="重排序模型配置")
    ocr_model: ModelConfig = Field(..., description="OCR模型配置")
    voice_to_text_model: ModelConfig | None = Field(
        ..., description="语音转文本模型配置"
    )
    video_to_text_model: ModelConfig | None = Field(
        ..., description="视频转文本模型配置"
    )
