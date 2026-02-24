import re
import asyncio
# 以下为保持和参考代码一致的依赖声明（实际使用时需确保这些模块存在）
from apps.parser.base_parser import BaseParser
from apps.enum.log import LogTypeEnum
from apps.schemas.log import LogModel


class PythonParser(BaseParser):
    """
    Python日志解析器：识别并分割Python脚本相关日志，排除其他编程语言日志干扰
    """
    log_type: LogTypeEnum = LogTypeEnum.PYTHON  # 需确保枚举中存在PYTHON类型
    prio = 60

    # 正向关键字：仅匹配Python自身特征，权重越高匹配优先级越高
    postive_keywords = {
        r'^\#!/usr/bin/env python': 20,          # Python脚本头（最高权重）
        r'^\#!/usr/bin/python': 20,              # Python脚本头
        r'Traceback \(most recent call last\):': 19,  # Python异常回溯头
        r'File ".*", line \d+, in .+': 19,       # Python文件行号信息
        # Python异常类型
        r'^(\w+Error|Exception|Warning|SyntaxError|IndentationError):': 18,
        r'^>>> \w+': 17,                         # Python交互提示符
        r'^\.\.\. \w+': 17,                      # Python多行输入提示符
        r'Exception in thread': 16,              # Python线程异常
        r'^import \w+|^from \w+ import': 15,     # Python导入语句
        r'^def \w+\(.*\):': 14,                  # Python函数定义
        r'^class \w+(\(.*\))?:': 14,             # Python类定义
        r'^\s*@\w+': 13,                         # Python装饰器
        r'^\s*if |^\s*elif |^\s*else:': 12,      # Python条件判断
        r'^\s*for \w+ in .+:': 12,               # Python for循环
        r'^\s*while .+:': 12,                    # Python while循环
        r'^\s*try:|^\s*except|^\s*finally:': 11,  # Python异常处理
        r'^\s*with .+ as .+:': 11,               # Python with语句
        r'print\(.*\)': 10,                      # Python print函数
        r'\bself\.\w+': 10,                      # Python类实例属性
        r'^\s*return ': 9,                       # Python返回语句
        r'^\s*yield ': 9,                        # Python生成器
        r'^ValueError|^TypeError|^KeyError|^IndexError': 9,  # 常见Python异常
    }

    # 负向关键字：排除其他编程语言日志，权重越高排除优先级越高
    negative_keywords = {
        # Bash日志（高权重排除）
        r'^\#!/bin/(ba|k)?sh': 5,
        r'line \d+: (syntax error|command not found)': 5,
        r'\bbash: \w+: No such file or directory': 5,
        # Java日志（高权重排除）
        r'Exception in thread ".*" java\.lang\.': 5,
        r'at \w+\.\w+\.\w+\(.*\.java:\d+\)': 5,
        r'Caused by: \w+\.\w+': 5,
        # C/C++日志（高权重排除）
        r'\#\d+ 0x[0-9a-fA-F]+ in \w+ at .+:\d+': 5,
        r'Segmentation fault \(core dumped\)': 5,
        # Go日志（高权重排除）
        r'goroutine \d+ \[(running|sleeping|waiting)\]': 5,
        r'panic: .+': 5,
        # JavaScript/Node.js（中权重排除）
        r'Error: .+\n\s+at .+:\d+:\d+': 5,
        r'ReferenceError: \w+ is not defined': 5,
        # PHP日志（中权重排除）
        r'PHP (Fatal|Warning|Notice) error:': 5,
        # 内核日志（中权重排除）
        r'localhost kernel:': 15,
        r'\[ *\d+\.\d+\] \w+:': 15,
        # 普通应用日志（低权重排除）
        r'nginx: \[error\]|mysqld: \[ERROR\]': 10,
    }

    # 连续Python日志的开头标志及其后续行判断依据
    mandatory = {
        # Python异常回溯头，后续是回溯详情
        r'Traceback \(most recent call last\):': [
            r'File ".*", line \d+, in .+',       # 回溯文件行号
            r'^(\w+Error|Exception): .+',        # 异常类型和信息
            r'^\s+',                              # 缩进的回溯上下文
        ],
        # Python函数定义头，后续是函数体
        r'^def \w+\(.*\):': [
            r'^\s+',                              # 函数体缩进
            r'^\s*\w+',                           # 函数内代码
            r'^\s*return |^\s*yield ',            # 返回/生成器语句
            r'^\s*if |^\s*for |^\s*while',        # 函数内控制结构
        ],
        # Python类定义头，后续是类体
        r'^class \w+(\(.*\))?:': [
            r'^\s+',                              # 类体缩进
            r'^\s*def \w+\(.*\):',                # 类内方法定义
            r'^\s*self\.',                        # 类内属性引用
            r'^\s*@\w+',                          # 类内装饰器
        ],
        # Python交互模式输入头，后续是交互内容
        r'^>>> \w+': [
            r'^\.\.\. \w+',                       # 多行输入续行
            r'^>>> \w+',                          # 连续交互命令
            r'^[\w\[\]\{\}\(\)]+',                # 交互执行结果
        ],
        # Python异常类型头，后续是异常详情
        r'^(\w+Error|Exception|Warning):': [
            r'^\s+',                              # 异常详情缩进
            r'File ".*", line \d+, in .+',       # 异常所在文件行号
            r'^(\w+Error|Exception): .+',        # 嵌套异常
        ],
    }

    @staticmethod
    async def _check_negative_keywords(log_lines: list[str]) -> bool:
        """异步检查负向关键字，存在则返回True"""
        for negative_pattern in PythonParser.negative_keywords.keys():
            if any(re.search(negative_pattern, line) for line in log_lines):
                return True
        return False

    @staticmethod
    async def _check_mandatory_patterns(log_lines: list[str]) -> bool:
        """异步检查mandatory核心头，匹配则返回True"""
        for mandatory_pattern, continuation_patterns in PythonParser.mandatory.items():
            for i, line in enumerate(log_lines):
                if re.search(mandatory_pattern, line):
                    # 找到mandatory头，检查后续行是否匹配continuation_patterns
                    for cont_pattern in continuation_patterns:
                        if i + 1 < len(log_lines) and re.search(cont_pattern, log_lines[i + 1]):
                            return True
        return False

    @staticmethod
    async def _check_positive_keywords(log_lines: list[str]) -> bool:
        """异步检查正向关键字，匹配则返回True"""
        for positive_pattern in PythonParser.positive_keywords.keys():
            if any(re.search(positive_pattern, line) for line in log_lines):
                return True
        return False

    @staticmethod
    async def is_matched(log_lines: list[str]) -> bool:
        """
        二次确认：精准匹配Python日志核心特征
        规则：1. 不含负向关键字 2. 匹配至少1个mandatory头 或 正向关键字
        """
        batch_size = 100000
        # 第一步：分批次异步检查负向关键字
        nagetive_tasks = []
        for i in range(0, len(log_lines), 3*batch_size):
            batch = log_lines[i:i+3*batch_size]
            j = 0
            while j < len(batch):
                sub_batch = batch[j:j+batch_size]
                nagetive_tasks.append(
                    PythonParser._check_negative_keywords(sub_batch))
                j += batch_size
            nagetive_results = await asyncio.gather(*nagetive_tasks)
            for result in nagetive_results:
                if result:
                    return False  # 存在负向关键字，直接排除

        # 第二步：分批次异步检查mandatory头
        mandatory_tasks = []
        for i in range(0, len(log_lines), 3*batch_size):
            batch = log_lines[i:i+3*batch_size]
            j = 0
            while j < len(batch):
                sub_batch = batch[j:j+batch_size]
                mandatory_tasks.append(
                    PythonParser._check_mandatory_patterns(sub_batch))
                j += batch_size
            mandatory_results = await asyncio.gather(*mandatory_tasks)
            for result in mandatory_results:
                if result:
                    return True  # 匹配到mandatory头，直接确认

        # 第三步：分批次异步检查正向关键字
        positive_tasks = []
        for i in range(0, len(log_lines), 3*batch_size):
            batch = log_lines[i:i+3*batch_size]
            j = 0
            while j < len(batch):
                sub_batch = batch[j:j+batch_size]
                positive_tasks.append(
                    PythonParser._check_positive_keywords(sub_batch))
                j += batch_size
            positive_results = await asyncio.gather(*positive_tasks)
            for result in positive_results:
                if result:
                    return True  # 匹配到正向关键字，确认为Python日志

        return False  # 未匹配到任何特征，排除为非Python日志

    @staticmethod
    async def split_logs(log_lines: list[str]) -> list[LogModel]:
        """
        分割Python日志：将连续的Python日志块合并，单行日志单独处理
        """
        results = []
        index = 0
        while index < len(log_lines):
            line = log_lines[index]
            # 检查是否匹配mandatory头（连续日志块起始）
            matched_mandatory = False
            for mandatory_pattern, continuation_patterns in PythonParser.mandatory.items():
                if re.search(mandatory_pattern, line):
                    matched_mandatory = True
                    # 提取完整的日志块
                    log_block = [line]
                    # 继续添加后续行直到不匹配continuation_patterns
                    for j in range(index + 1, len(log_lines)):
                        if any(re.search(pat, log_lines[j]) for pat in continuation_patterns):
                            log_block.append(log_lines[j])
                        elif log_lines[j].strip() == '':  # 允许空行作为日志块间隔
                            log_block.append(log_lines[j])
                        else:
                            break
                    # 添加到结果
                    results.append(LogModel(
                        log_type=LogTypeEnum.PYTHON,
                        offset=index,
                        content="\n".join(log_block)
                    ))
                    # 跳过已处理的行
                    index += len(log_block)
                    break

            # 如果不是连续日志块，单独处理单行
            if not matched_mandatory:
                results.append(LogModel(
                    log_type=LogTypeEnum.PYTHON,
                    offset=index,
                    content=line
                ))
                index += 1

        return results
