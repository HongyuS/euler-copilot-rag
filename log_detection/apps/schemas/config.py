from pydantic import BaseModel, Field
from apps.enum.provider import ProviderEnum


class EmbeddingModelConfig(BaseModel):
    provider: ProviderEnum = Field(
        default=ProviderEnum.OPENAPI, description="embedding模型的供应商", alias="EMBEDDING_PROVIDER")
    end_point: str = Field(default="http://exapmle.com",
                           pattern="http(s)?://([\w-]+\\.)+[\w-]+(:\\d+)?(/\\S*)?", description="embedding模型的endpoint", alias="EMBEDDING_END_POINT")
    api_key: str = Field(default="your_api_key",
                         description="embedding模型的api_key", alias="EMBEDDING_API_KEY")
    model_name: str = Field(default="your_model_name",
                            description="embedding模型的名称", alias="EMBEDDING_MODEL_NAME")


class LLMModelConfig(BaseModel):
    provider: ProviderEnum = Field(
        default=ProviderEnum.OPENAPI, description="LLM模型的供应商", alias="LLM_PROVIDER")
    end_point: str = Field(default="http://exapmle.com",
                           pattern="http(s)?://([\w-]+\\.)+[\w-]+(:\\d+)?(/\\S*)?", description="LLM模型的endpoint", alias="LLM_END_POINT")
    api_key: str = Field(default="your_api_key",
                         description="LLM模型的api_key", alias="LLM_API_KEY")
    model_name: str = Field(default="your_model_name",
                            description="LLM模型的名称", alias="LLM_MODEL_NAME")


class ConfigModel(BaseModel):
    log_pare_use_cpu_limit: int | None = Field(
        default=None, description="日志解析服务使用的CPU上限", alias="LOG_PARE_USE_CPU_LIMIT")
    sql_lite_db_path: str = Field(
        default="sqlite_multi_process.db", description="SQLite数据库文件路径", alias="SQL_LITE_DB_PATH")
    embedding_model: EmbeddingModelConfig = Field(
        default=EmbeddingModelConfig(), description="embedding模型配置", alias="EMBEDDING_MODEL")
    llm_model: LLMModelConfig = Field(
        default=LLMModelConfig(), description="LLM模型配置", alias="LLM_MODEL")
