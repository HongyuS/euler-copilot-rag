import uuid
import json
from pydantic import Field
import asyncio
from mcp.server import FastMCP
from src.config.config import Config
from src.service.log import LogTaskHandleService
from src.enum.task import TaskTypeEnum
from src.sqlite.sqlite import AsyncSQLiteSingleton
from src.service.task import TaskService

host = Config().get_config().run_config.host
port = Config().get_config().run_config.port
mcp = FastMCP("Log Detect MCP Server", host=host, port=port)


@mcp.tool(
    name="create_log_parse_task",
    description="""
    这是创建日志解析任务的工具函数，前端会调用这个接口来创建日志解析任务。参数包括：
    - task_type: 任务类型，枚举值包括：base（基础版本，直接返回日志内容，不进行异常检测）、log_detection_base_on_keywords（基于关键词的日志检测）、log_detection_base_on_clustering（基于聚类的日志检测）、log_detection_base_on_llm（基于LLM的日志检测）,log_detection_base_on_embedding_keywords(基于embedding和关键字的日志检测),也可以者不传，默认为配置文件中设置的日志解析方法
    - query: 查询语句，用于描述当前的异常现象或者需要关注的日志内容，基于这个查询语句，日志检测Worker会进行日志异常检测
    - file_path_list: 日志文件路径列表，包含需要进行日志检测的日志文件的路径
    - max_anomaly_log_count: 最大异常日志数量，日志检测Worker会根据这个数量来限制返回的异常日志的数量，确保不会返回过多的异常日志
    - anomaly_keywords: 异常关键词列表，基于关键词的日志检测Worker会使用这个异常关键词列表来进行日志的异常检测
    - time_start: 日志时间范围的起始时间，格式为 "YYYY-MM-DD HH:MM"，日志检测Worker会基于这个时间范围来过滤日志，确保只检测这个时间范围内的日志
    - time_end: 日志时间范围的结束时间，格式为 "YYYY-MM-DD HH:MM"，日志检测Worker会基于这个时间范围来过滤日志，确保只检测这个时间范围内的日志
    这个函数会返回创建的任务ID（uuid4格式），前端可以基于这个任务ID来查询任务的执行状态和结果。返回格式如下：
    {
        "task_id": "生成的任务ID，uuid4格式"
    }
    """,
)
async def create_log_parse_task(
    task_type: TaskTypeEnum | None = None,
    query: str = Field(
        default="",
        description="查询语句，用于描述当前的异常现象或者需要关注的日志内容，基于这个查询语句，日志检测Worker会进行日志异常检测",
    ),
    file_path_list: list[str] = Field(
        default_factory=list,
        description="日志文件路径列表，包含需要进行日志检测的日志文件的路径",
    ),
    max_anomaly_log_count: int = Field(
        default=64,
        description="最大异常日志数量，日志检测Worker会根据这个数量来限制返回的异常日志的数量，确保不会返回过多的异常日志",
    ),
    anomaly_keywords: list[str] = Field(
        default_factory=list,
        description="异常关键词列表，基于关键词的日志检测Worker会使用这个异常关键词列表来进行日志的异常检测",
    ),
    time_start: str | None = Field(
        default=None,
        description="日志时间范围的起始时间，格式为 'YYYY-MM-DD HH:MM'",
        pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$",
    ),
    time_end: str | None = Field(
        default=None,
        description="日志时间范围的结束时间，格式为 'YYYY-MM-DD HH:MM'",
        pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$",
    ),
) -> str:
    task_id = await LogTaskHandleService.create_log_parse_task(
        task_type=task_type,
        query=query,
        file_path_list=file_path_list,
        max_anomaly_log_count=max_anomaly_log_count,
        anomaly_keywords=anomaly_keywords,
        time_start=time_start,
        time_end=time_end,
    )
    return json.dumps({"task_id": task_id})


@mcp.tool(
    name="get_task_message",
    description="""
    这是获取任务信息的工具函数，前端会调用这个接口来获取任务的执行状态和相关信息。参数包括：
- task_id: 任务ID，uuid4格式
这个函数会返回任务的相关信息，包括：任务ID、任务名称、任务类型、任务完成百分比、任务状态、任务相关参数、任务创建时间。返回格式如下：
{
    "task_id": "任务ID，uuid4格式",
    "task_name": "任务名称",
    "task_type": "任务类型",
    "compltetion_precent": 任务完成百分比，float类型,
    "status": "任务状态",
    "task_related_params": "任务相关参数，json字符串格式",
    "created_at": "任务创建时间，格式为 'YYYY-MM-DD HH:MM:SS'"
}
    """,
)
async def get_task_status(
    task_id: uuid.UUID = Field(description="任务ID，uuid4格式"),
) -> str:
    task_model = await LogTaskHandleService.get_task_message(task_id)
    if task_model is None:
        raise ValueError(f"任务 {task_id} 不存在")
    return json.dumps(task_model.model_dump(exclude_none=True))


@mcp.tool(
    name="stop_task",
    description="""
    这是停止任务的工具函数，前端会调用这个接口来停止正在执行的任务。参数包括：
    - task_id: 任务ID，uuid4格式
    这个函数会返回一个布尔值，表示是否成功停止了任务。返回格式如下：
    {
        "success": true // 如果成功停止了任务，则为true；如果没有成功停止任务（例如任务已经完成或者不存在），则为false
    }
""",
)
async def stop_task(
    task_id: uuid.UUID = Field(description="任务ID，uuid4格式"),
) -> str:
    success = await LogTaskHandleService.stop_task(task_id)
    return json.dumps({"success": success})


@mcp.tool(
    name="get_task_result",
    description="""
    这是获取任务结果的工具函数，前端会调用这个接口来获取任务的执行结果。参数包括：
- task_id: 任务ID，uuid4格式
- offset: 偏移量，整数类型，表示从第几条结果开始返回，用于分页查询
- limit: 返回结果的数量，整数类型，表示一次返回多少条结果，用于分页查询
- is_anomalous: 是否只返回异常日志，布尔类型，如果为true，则只返回异常日志；如果为false，则返回所有日志；如果不传，则默认返回所有日志
这个函数会返回任务的执行结果，包括总结果数量和结果列表。结果列表中的每个元素包含：日志文件路径、任务ID、异常原因（如果是异常日志则有值，否则为null）、异常分数（如果是异常日志则有值，否则为null）。返回格式如下：
{
    "total": 总结果数量，整数类型,
    "results": [
        {
            "id": "日志解析结果ID，uuid4格式",
            "file_path": "日志文件路径",
            "task_id": "任务ID，uuid4格式",
            "is_anomalous": "日志是否异常，布尔类型",
            "content": "日志内容，字符串类型",
            "anomaly_reason": "日志异常原因，如果日志不异常，则返回空字符串",
            "anomaly_score": "日志异常分数，如果日志不异常，则返回0.0"
        },
        ...
    ]
""",
)
#加关键字匹配
async def get_task_result(
    task_id: uuid.UUID = Field(description="任务ID，uuid4格式"),
    offset: int | None = Field(
        default=None,
        description="偏移量，整数类型，表示从第几条结果开始返回，用于分页查询",
    ),
    limit: int | None = Field(
        default=None,
        description="返回结果的数量，整数类型，表示一次返回多少条结果，用于分页查询",
    ),
    is_anomalous: bool | None = Field(
        default=None,
        description="是否只返回异常日志，布尔类型，如果为true，则只返回异常日志；如果为false，则返回所有日志；如果不传，则默认返回所有日志",
    ),
) -> str:
    total, log_parse_result_models = await LogTaskHandleService.get_task_result(
        task_id, limit, offset, is_anomalous
    )
    return json.dumps({
        "total": total,
        "results": [
            log_parse_result_model.model_dump(exclude_none=True)
            for log_parse_result_model in log_parse_result_models
        ],
    })


# 定义异步主函数，统一管理异步任务和MCP服务器启动


def init():
    AsyncSQLiteSingleton()._sync_init_database()
    asyncio.run(TaskService.update_running_tasks_to_pending_tasks())


if __name__ == "__main__":
    init()
    try:
        listener = TaskService.run_task_listener_in_process()
        mcp.run(transport="sse")
    except Exception as e:
        print(f"启动MCP Server失败，错误信息：{e}")
    finally:
        import os
        import signal
        print(f"任务监听进程ID：{listener.pid}")
        if listener.pid is not None:
            os.kill(listener.pid, signal.SIGKILL)
        print(f"任务监听进程ID：{listener.pid} 已被终止")
