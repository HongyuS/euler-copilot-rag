# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""
YAML 解析器测试

测试范围:
- YAML 文件解析
- 嵌套结构处理
- 数据类型支持
"""

from pathlib import Path

import pytest
import yaml

from data_chain.parser.handler.yaml_parser import YamlParser
from data_chain.parser.parse_result import ParseResult
from data_chain.entities.enum import ChunkType, DocParseRelutTopology, ChunkParseTopology


class TestYamlParserBasic:
    """测试 YAML 解析器基本功能"""

    @pytest.mark.asyncio
    async def test_parse_simple_mapping(self, temp_dir):
        """测试解析简单映射"""
        test_file = temp_dir / "simple.yaml"
        data = {
            'name': 'OpenEuler',
            'version': '22.03',
            'arch': 'x86_64'
        }
        test_file.write_text(yaml.dump(data), encoding="utf-8")
        
        try:
            result = await YamlParser.parser(str(test_file))
            
            assert isinstance(result, ParseResult)
            assert result.parse_topology_type == DocParseRelutTopology.LIST
            assert len(result.nodes) == 1
            assert result.nodes[0].content['name'] == 'OpenEuler'
        finally:
            test_file.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_parse_nested_structure(self, temp_dir):
        """测试解析嵌套结构"""
        test_file = temp_dir / "nested.yaml"
        data = {
            'os': {
                'name': 'OpenEuler',
                'kernel': {
                    'version': '5.10',
                    'config': 'default'
                }
            },
            'packages': ['vim', 'git', 'docker']
        }
        test_file.write_text(yaml.dump(data), encoding="utf-8")
        
        try:
            result = await YamlParser.parser(str(test_file))
            
            assert len(result.nodes) == 1
            content = result.nodes[0].content
            assert content['os']['kernel']['version'] == '5.10'
            assert 'vim' in content['packages']
        finally:
            test_file.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_parse_list(self, temp_dir):
        """测试解析列表"""
        test_file = temp_dir / "list.yaml"
        data = [
            {'name': 'item1', 'value': 100},
            {'name': 'item2', 'value': 200},
        ]
        test_file.write_text(yaml.dump(data), encoding="utf-8")
        
        try:
            result = await YamlParser.parser(str(test_file))
            
            assert len(result.nodes) == 1
            assert isinstance(result.nodes[0].content, list)
            assert len(result.nodes[0].content) == 2
        finally:
            test_file.unlink(missing_ok=True)


class TestYamlParserDataTypes:
    """测试 YAML 数据类型"""

    @pytest.mark.asyncio
    async def test_parse_various_types(self, temp_dir):
        """测试各种数据类型"""
        test_file = temp_dir / "types.yaml"
        yaml_content = """
string_value: "Hello"
integer_value: 42
float_value: 3.14
boolean_true: true
boolean_false: false
null_value: null
datetime: 2024-01-01 12:00:00
multiline: |
  Line 1
  Line 2
  Line 3
"""
        test_file.write_text(yaml_content, encoding="utf-8")
        
        try:
            result = await YamlParser.parser(str(test_file))
            
            content = result.nodes[0].content
            assert content['string_value'] == "Hello"
            assert content['integer_value'] == 42
            assert content['float_value'] == 3.14
            assert content['boolean_true'] is True
            assert content['boolean_false'] is False
            assert content['null_value'] is None
        finally:
            test_file.unlink(missing_ok=True)


class TestYamlParserErrorHandling:
    """测试错误处理"""

    @pytest.mark.asyncio
    async def test_parse_invalid_yaml(self, temp_dir):
        """测试解析无效 YAML"""
        test_file = temp_dir / "invalid.yaml"
        test_file.write_text("invalid: yaml: content: [", encoding="utf-8")
        
        try:
            with pytest.raises(Exception):
                await YamlParser.parser(str(test_file))
        finally:
            test_file.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        with pytest.raises(Exception):
            await YamlParser.parser("/nonexistent/file.yaml")


class TestYamlParserNodeStructure:
    """测试节点结构"""

    @pytest.mark.asyncio
    async def test_node_properties(self, temp_dir):
        """测试节点属性"""
        test_file = temp_dir / "test.yaml"
        test_file.write_text("key: value", encoding="utf-8")
        
        try:
            result = await YamlParser.parser(str(test_file))
            
            node = result.nodes[0]
            assert node.lv == 0
            assert node.type == ChunkType.JSON
            assert node.parse_topology_type == ChunkParseTopology.GERNERAL
            assert node.link_nodes == []
        finally:
            test_file.unlink(missing_ok=True)


class TestYamlParserComplexStructures:
    """测试复杂结构"""

    @pytest.mark.asyncio
    async def test_parse_ansible_style(self, temp_dir):
        """测试 Ansible 风格的 YAML"""
        test_file = temp_dir / "ansible.yaml"
        yaml_content = """
---
- name: Install packages
  hosts: all
  tasks:
    - name: Install nginx
      package:
        name: nginx
        state: present
    - name: Start service
      service:
        name: nginx
        state: started
"""
        test_file.write_text(yaml_content, encoding="utf-8")
        
        try:
            result = await YamlParser.parser(str(test_file))
            
            assert len(result.nodes) == 1
            content = result.nodes[0].content
            assert isinstance(content, list)
            assert len(content) == 1
            assert 'tasks' in content[0]
        finally:
            test_file.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_parse_docker_compose(self, temp_dir):
        """测试 Docker Compose 风格的 YAML"""
        test_file = temp_dir / "docker-compose.yaml"
        yaml_content = """
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    environment:
      - NGINX_HOST=localhost
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: mydb
"""
        test_file.write_text(yaml_content, encoding="utf-8")
        
        try:
            result = await YamlParser.parser(str(test_file))
            
            content = result.nodes[0].content
            assert 'services' in content
            assert 'web' in content['services']
            assert 'db' in content['services']
        finally:
            test_file.unlink(missing_ok=True)
