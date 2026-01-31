# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.

from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class PermissionDeniedException(HTTPException):
    """权限拒绝异常类

    用于处理用户权限不足的情况，返回403状态码而不是500内部服务器错误
    """

    def __init__(
        self,
        detail: str = "用户没有权限执行此操作",
        headers: Optional[Dict[str, Any]] = None,
        retcode: int = 403,
        rtmsg: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers
        )
        self.retcode = retcode
        self.rtmsg = rtmsg or detail


class TeamPermissionDeniedException(PermissionDeniedException):
    """团队权限拒绝异常"""

    def __init__(self, action: str = "访问团队", team_id: str = None):
        detail = f"用户没有权限{action}"
        if team_id:
            detail += f"（团队ID: {team_id}）"
        super().__init__(detail=detail)


class KnowledgeBasePermissionDeniedException(PermissionDeniedException):
    """知识库权限拒绝异常"""

    def __init__(self, action: str = "访问知识库", kb_id: str = None):
        detail = f"用户没有权限{action}"
        if kb_id:
            detail += f"（知识库ID: {kb_id}）"
        super().__init__(detail=detail)


class DocumentPermissionDeniedException(PermissionDeniedException):
    """文档权限拒绝异常"""

    def __init__(self, action: str = "访问文档", doc_id: str = None):
        detail = f"用户没有权限{action}"
        if doc_id:
            detail += f"（文档ID: {doc_id}）"
        super().__init__(detail=detail)


class DatasetPermissionDeniedException(PermissionDeniedException):
    """数据集权限拒绝异常"""

    def __init__(self, action: str = "访问数据集", dataset_id: str = None):
        detail = f"用户没有权限{action}"
        if dataset_id:
            detail += f"（数据集ID: {dataset_id}）"
        super().__init__(detail=detail)


class RolePermissionDeniedException(PermissionDeniedException):
    """角色权限拒绝异常"""

    def __init__(self, action: str = "管理角色", role_id: str = None):
        detail = f"用户没有权限{action}"
        if role_id:
            detail += f"（角色ID: {role_id}）"
        super().__init__(detail=detail)


class TaskPermissionDeniedException(PermissionDeniedException):
    """任务权限拒绝异常"""

    def __init__(self, action: str = "访问任务", task_id: str = None):
        detail = f"用户没有权限{action}"
        if task_id:
            detail += f"（任务ID: {task_id}）"
        super().__init__(detail=detail)


class TestingPermissionDeniedException(PermissionDeniedException):
    """测试权限拒绝异常"""

    def __init__(self, action: str = "访问测试", testing_id: str = None):
        detail = f"用户没有权限{action}"
        if testing_id:
            detail += f"（测试ID: {testing_id}）"
        super().__init__(detail=detail)


class ChunkPermissionDeniedException(PermissionDeniedException):
    """分片权限拒绝异常"""

    def __init__(self, action: str = "访问分片", chunk_id: str = None):
        detail = f"用户没有权限{action}"
        if chunk_id:
            detail += f"（分片ID: {chunk_id}）"
        super().__init__(detail=detail)


class MessagePermissionDeniedException(PermissionDeniedException):
    """消息权限拒绝异常"""

    def __init__(self, action: str = "操作消息", message_id: str = None):
        detail = f"用户没有权限{action}"
        if message_id:
            detail += f"（消息ID: {message_id}）"
        super().__init__(detail=detail)
