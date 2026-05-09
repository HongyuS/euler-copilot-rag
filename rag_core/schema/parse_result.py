from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import uuid4
from ENUM.parse import ParseResultTopology, ChunkType, ChunkParseTopology


class ParseNode(BaseModel):
    """
    解析节点
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    content: str = Field(..., description="节点内容")
    type: ChunkType = Field(..., description="节点类型")
    text: str = Field(default="", description="节点文本")
    content: Any = Field(..., description="节点内容")
    text_feature: str = Field(default="", description="节点特征")
    vector: Optional[list[float]] = Field(default=None, description="节点向量")
    bbox: Optional[tuple[float, float, float, float]] = Field(
        default=None, description="节点位置，格式为(x0, y0, x1, y1)"
    )


class ParseResult(BaseModel):
    """
    解析结果
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="唯一ID")
    page_cnt: int = Field(..., description="页数")
    parse_result_topology: ParseResultTopology = Field(..., description="解析结果拓扑")
    parse_nodes: list[ParseNode] = Field(..., description="解析树节点列表")
    edges: list[tuple[str, str]] = Field(..., description="有向边列表")
