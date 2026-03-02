from pydantic import BaseModel, Field
from apps.enum.provider import ProviderEnum
from apps.enum.ocr import OcrMethodEnum
from apps.enum.task import TaskTypeEnum


class EmbeddingModelConfig(BaseModel):
    provider: ProviderEnum = Field(
        default=ProviderEnum.OPENAPI, description="embedding模型的供应商", alias="EMBEDDING_PROVIDER")
    end_point: str = Field(default="http://exapmle.com",
                           pattern="http(s)?://([\w-]+\\.)+[\w-]+(:\\d+)?(/\\S*)?", description="embedding模型的endpoint", alias="EMBEDDING_END_POINT")
    api_key: str = Field(default="your_api_key",
                         description="embedding模型的api_key", alias="EMBEDDING_API_KEY")
    model_name: str = Field(default="your_model_name",
                            description="embedding模型的名称", alias="EMBEDDING_MODEL_NAME")
    batch_size: int = Field(
        default=32, description="批量处理日志时的批大小", alias="EMBEDDING_BATCH_SIZE")


class LLMModelConfig(BaseModel):
    provider: ProviderEnum = Field(
        default=ProviderEnum.OPENAPI, description="LLM模型的供应商", alias="LLM_PROVIDER")
    end_point: str = Field(default="http://exapmle.com",
                           pattern="http(s)?://([\w-]+\\.)+[\w-]+(:\\d+)?(/\\S*)?", description="LLM模型的endpoint", alias="LLM_END_POINT")
    api_key: str = Field(default="your_api_key",
                         description="LLM模型的api_key", alias="LLM_API_KEY")
    model_name: str = Field(default="your_model_name",
                            description="LLM模型的名称", alias="LLM_MODEL_NAME")
    max_tokens: int = Field(
        default=2048, description="LLM模型生成文本的最大token数量", alias="LLM_MAX_TOKENS")
    batch_size: int = Field(
        default=32, description="批量处理日志时的批大小", alias="LLM_BATCH_SIZE")


class RunConfig(BaseModel):
    host: str = Field(default="0.0.0.0",
                      description="服务运行的主机地址", alias="RUN_HOST")
    port: int = Field(default=12144, description="服务运行的端口号", alias="RUN_PORT")


class OcrConfig(BaseModel):
    method: OcrMethodEnum = Field(
        default=OcrMethodEnum.OFFLINE, description="OCR识别方法，online表示使用在线OCR API，offline表示使用本地OCR模型", alias="OCR_METHOD")
    api_url: str = Field(
        default="", description="在线OCR API的URL地址，当method为online时需要配置", alias="OCR_API_URL")


class ConfigModel(BaseModel):
    log_parse_method: TaskTypeEnum = Field(
        default=TaskTypeEnum.LOG_DETECTION_BASE_ON_LLM, description="日志解析方法，枚举值包括：base（基础版本，直接返回日志内容，不进行异常检测）、log_detection_base_on_keywords（基于关键词的日志检测）、log_detection_base_on_clustering（基于聚类的日志检测）、log_detection_base_on_llm（基于LLM的日志检测）", alias="LOG_PARSE_METHOD")
    sql_lite_db_path: str = Field(
        default="log_detection_multi_process.db", description="SQLite数据库文件路径", alias="SQL_LITE_DB_PATH")
    embedding_model: EmbeddingModelConfig = Field(
        default=EmbeddingModelConfig(), description="embedding模型配置", alias="EMBEDDING_MODEL")
    llm_model: LLMModelConfig = Field(
        default=LLMModelConfig(), description="LLM模型配置", alias="LLM_MODEL")
    run_config: RunConfig = Field(
        default=RunConfig(), description="服务运行配置", alias="RUN_CONFIG")
    ocr_config: OcrConfig = Field(
        default=OcrConfig(), description="OCR配置", alias="OCR_CONFIG")
