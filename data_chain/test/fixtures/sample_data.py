# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
测试数据生成器

提供各种测试数据的生成函数。
"""

import json
import uuid
from typing import Any


class SampleDataGenerator:
    """样本数据生成器"""

    @staticmethod
    def generate_txt_content(
        paragraphs: int = 5,
        sentences_per_paragraph: int = 3,
        topic: str = "OpenEuler"
    ) -> str:
        """生成文本内容"""
        template_sentences = [
            f"{topic} 是一个优秀的开源操作系统。",
            f"{topic} 支持多种处理器架构。",
            f"{topic} 拥有强大的社区支持。",
            f"{topic} 提供企业级的稳定性和安全性。",
            f"{topic} 广泛应用于云计算和边缘计算场景。",
            f"{topic} 的生态系统日益完善。",
            f"{topic} 为用户提供了丰富的软件包。",
            f"{topic} 持续进行技术创新。",
        ]
        
        paragraphs_list = []
        for _ in range(paragraphs):
            sentences = []
            for i in range(sentences_per_paragraph):
                sentence_idx = i % len(template_sentences)
                sentences.append(template_sentences[sentence_idx])
            paragraphs_list.append("".join(sentences))
        
        return "\n\n".join(paragraphs_list)

    @staticmethod
    def generate_json_data(
        items_count: int = 10,
        nested_level: int = 2
    ) -> dict:
        """生成 JSON 数据"""
        def create_nested(level: int) -> Any:
            if level == 0:
                return {
                    "value": f"value_{uuid.uuid4().hex[:8]}",
                    "number": 42,
                    "flag": True
                }
            return {
                "name": f"level_{level}",
                "children": [create_nested(level - 1) for _ in range(3)]
            }
        
        return {
            "id": str(uuid.uuid4()),
            "name": "OpenEuler Data",
            "items": [create_nested(nested_level) for _ in range(items_count)],
            "metadata": {
                "version": "1.0",
                "count": items_count
            }
        }

    @staticmethod
    def generate_markdown_document(
        sections: int = 5,
        with_code: bool = True,
        with_table: bool = True
    ) -> str:
        """生成 Markdown 文档"""
        lines = ["# OpenEuler 文档", ""]
        
        for i in range(1, sections + 1):
            lines.extend([
                f"## 第 {i} 节",
                "",
                f"这是第 {i} 节的详细介绍。OpenEuler 在这个方面表现出色。",
                "",
                "### 特性",
                "",
                "- 高性能",
                "- 高可靠性",
                "- 良好的兼容性",
                "",
            ])
            
            if with_code and i % 2 == 0:
                lines.extend([
                    "### 示例代码",
                    "",
                    "```bash",
                    f"# 安装软件包 {i}",
                    "dnf install package-name",
                    "",
                    "# 启动服务",
                    "systemctl start service",
                    "```",
                    "",
                ])
            
            if with_table and i % 3 == 0:
                lines.extend([
                    "### 参数表",
                    "",
                    "| 参数 | 说明 | 默认值 |",
                    "|------|------|--------|",
                    "| param1 | 参数1 | value1 |",
                    "| param2 | 参数2 | value2 |",
                    "",
                ])
        
        lines.extend([
            "## 总结",
            "",
            "OpenEuler 是一个值得信赖的操作系统选择。",
        ])
        
        return "\n".join(lines)

    @staticmethod
    def generate_search_query_variations() -> list[str]:
        """生成搜索查询变体"""
        return [
            "OpenEuler 开源操作系统",
            "OpenEuler 安装指南",
            "OpenEuler 系统配置",
            "OpenEuler 软件包管理",
            "OpenEuler 内核参数",
            "OpenEuler 网络配置",
            "OpenEuler 安全设置",
            "OpenEuler 性能优化",
            "OpenEuler 故障排查",
            "OpenEuler 最佳实践",
        ]

    @staticmethod
    def generate_mock_chunks(
        count: int = 10,
        kb_id: uuid.UUID = None
    ) -> list[dict]:
        """生成模拟 chunk 数据"""
        if kb_id is None:
            kb_id = uuid.uuid4()
        
        chunks = []
        doc_ids = [uuid.uuid4() for _ in range(max(1, count // 3))]
        
        contents = [
            "OpenEuler 是一个开源操作系统，支持 x86、ARM 和 RISC-V 架构。",
            "OpenEuler 提供企业级的稳定性和安全性保障。",
            "OpenEuler 社区活跃，拥有大量的开发者和用户。",
            "OpenEuler 支持容器和 Kubernetes 编排。",
            "OpenEuler 的安装过程简单快捷，适合各种场景。",
            "OpenEuler 的软件仓库包含丰富的应用程序。",
            "OpenEuler 的内核经过优化，性能表现优异。",
            "OpenEuler 提供完善的技术文档和支持。",
            "OpenEuler 定期发布安全更新和补丁。",
            "OpenEuler 适用于云计算、边缘计算和嵌入式系统。",
        ]
        
        for i in range(count):
            chunks.append({
                "id": uuid.uuid4(),
                "kb_id": kb_id,
                "doc_id": doc_ids[i % len(doc_ids)],
                "doc_name": f"document_{i % len(doc_ids)}.txt",
                "text": contents[i % len(contents)],
                "tokens": 20 + i * 2,
                "global_offset": i,
            })
        
        return chunks


# 预定义的测试数据
SAMPLE_TXT_CONTENT = """# OpenEuler 操作系统

OpenEuler 是一个开源操作系统，支持多样性计算。

## 核心特性

OpenEuler 支持 ARM、x86、RISC-V 等多种处理器架构。
OpenEuler 提供企业级稳定性和安全性。
OpenEuler 拥有活跃的社区生态。

## 应用场景

OpenEuler 广泛应用于云计算场景。
OpenEuler 适用于边缘计算环境。
OpenEuler 支持嵌入式系统部署。

## 技术架构

OpenEuler 采用模块化设计。
OpenEuler 支持容器化部署。
OpenEuler 兼容 Kubernetes 编排。
"""

SAMPLE_JSON_DATA = {
    "name": "OpenEuler",
    "version": "22.03 LTS",
    "architectures": ["x86_64", "aarch64", "riscv64"],
    "features": {
        "security": True,
        "container": True,
        "virtualization": True,
        "kubernetes": True
    },
    "packages": [
        {"name": "kernel", "version": "5.10.0"},
        {"name": "glibc", "version": "2.34"},
        {"name": "gcc", "version": "10.3.1"}
    ],
    "repositories": [
        "OS",
        "EPOL",
        "debuginfo",
        "source"
    ]
}

SAMPLE_MARKDOWN_CONTENT = """# OpenEuler 使用指南

欢迎使用 OpenEuler 操作系统！

## 安装

### 系统要求

- CPU: x86_64 或 ARM64
- 内存: 至少 2GB
- 磁盘: 至少 20GB 可用空间

### 安装步骤

1. 下载 ISO 镜像
2. 制作启动盘
3. 启动安装程序
4. 配置系统参数

## 配置

### 网络设置

```bash
# 配置静态 IP
nmcli con mod eth0 ipv4.addresses 192.168.1.100/24
nmcli con mod eth0 ipv4.gateway 192.168.1.1
nmcli con up eth0
```

### 软件源配置

| 源名称 | 地址 | 用途 |
|--------|------|------|
| OS | https://repo.openeuler.org | 基础系统 |
| EPOL | https://repo.openeuler.org/epol | 扩展软件 |

## 常用命令

| 命令 | 说明 |
|------|------|
| dnf install | 安装软件包 |
| dnf update | 更新系统 |
| systemctl | 服务管理 |

## 故障排查

如遇问题，请查看日志文件：

- /var/log/messages
- /var/log/dnf.log
- /var/log/secure
"""
