from pydantic import BaseModel, Field
from apps.enum.provider import ProviderEnum


class EmbeddingModelConfig(BaseModel):
    provider: ProviderEnum = Field(
        default=ProviderEnum.OPENAPI, description="embedding模型的供应商")
    end_point: str = Field(default="http://exapmle.com",
                           pattern="http(s)?://([\w-]+\\.)+[\w-]+(:\\d+)?(/\\S*)?", description="embedding模型的endpoint")
    api_key: str = Field(default="your_api_key",
                         description="embedding模型的api_key")
    model_name: str = Field(default="your_model_name",
                            description="embedding模型的名称")


class LLMModelConfig(BaseModel):
    provider: ProviderEnum = Field(
        default=ProviderEnum.OPENAPI, description="LLM模型的供应商")
    end_point: str = Field(default="http://exapmle.com",
                           pattern="http(s)?://([\w-]+\\.)+[\w-]+(:\\d+)?(/\\S*)?", description="LLM模型的endpoint")
    api_key: str = Field(default="your_api_key",
                         description="LLM模型的api_key")
    model_name: str = Field(default="your_model_name",
                            description="LLM模型的名称")


class ConfigModel(BaseModel):
    log_pare_use_cpu_limit: int | None = Field(
        default=None, description="日志解析服务使用的CPU上限")
    sql_lite_db_path: str = Field(
        default="sqlite_multi_process.db", description="SQLite数据库文件路径")
    embedding_model_list: list[EmbeddingModelConfig] = Field(
        default=[], description="embedding模型配置列表")
    llm_model: LLMModelConfig = Field(
        default=LLMModelConfig(), description="LLM模型配置")
