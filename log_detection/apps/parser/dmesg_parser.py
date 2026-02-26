import re
import asyncio
from apps.parser.base_parser import BaseParser
from apps.enum.log import LogTypeEnum
from apps.schemas.log import LogModel


class DMESGParser(BaseParser):
    """
    StackParser
    """
    log_type: LogTypeEnum = LogTypeEnum.DMESG
    prio = 100
    # 正向关键字：匹配dmesg内核日志核心特征，权重越高匹配优先级越高
    postive_keywords = {
        r'localhost kernel:': 20,          # 经典syslog格式dmesg头（最高权重）
        r'\[ *\d+\.\d+\] \w+:': 15,        # dmesg标准时间戳+子系统（如[123.456] ext4:）
        r'\[ *\d+\.\d+\]\s*Call Trace:': 18,  # 带时间戳的核心栈头（高权重）
        r'\[ *\d+\.\d+\]\s*Oops:': 18,     # 带时间戳的Oops崩溃（高权重）
        r'\[ *\d+\.\d+\]\s*panic:': 18,    # 带时间戳的panic崩溃（高权重）
        r'kernel: \[ *\d+\.\d+\]': 15,     # 反向格式syslog（kernel: [123.456]）
        r'CPU: \d+ PID: \d+ Comm:': 12,    # dmesg崩溃核心上下文
        r'Backtrace:\s*$': 12,             # 嵌入式内核回溯头
        r'\+\+\+ killed by KASAN \+\+\+': 12,  # KASAN内存检测崩溃标识
        r'\[\<[0-9a-fA-F]+\>\]': 10,       # x86架构栈地址格式
        r'pc : |lr : |elr_el1:': 10,       # ARM/ARM64架构寄存器标识
    }

    # 负向关键字：排除非dmesg日志，权重越高排除优先级越高
    negative_keywords = {
        # 多语言用户态异常（高权重排除）
        r'Traceback \(most recent call last\):': 10,
        r'Exception in thread': 10,
        r'goroutine \d+ \[(running|sleeping|waiting)': 10,
        r'at \w+\.\w+\.\w+<span data-type="inline-math" data-value="W0EtWmEtejAtOV0rXC5qYXZhOlxkKw=="></span>': 10,
        r'\#\d+ 0x[0-9a-fA-F]+ in \w+ at .+:\d+': 10,
        r'PHP (Fatal|Warning|Notice) error:': 10,
        r'Error: .+\n\s+at .+:\d+:\d+': 10,  # JS/Node.js异常
        # 脚本执行错误（中权重排除）
        r'^\#!/bin/(ba|k)?sh': 5,
        r'^set -[xe]': 5,
        r'line \d+: (syntax error|command not found|unbound variable)': 5,
        r'^\+ \w+': 5,
        r'\bbash: \w+: No such file or directory': 5,
        r'\bsh: \d+: \w+: not found': 5,
        r'\bbash: .+: Permission denied': 5,
        r'\/bin\/sh: .+ not found': 5,
        # 普通系统/应用日志（低权重排除，避免误删）
        r'^\w+ <span data-type="inline-math" data-value="cGlkIFxkKw=="></span>:': 3,           # 普通进程日志
        r'nginx: \[error\]': 3,            # Nginx应用错误
        r'mysqld: \[ERROR\]': 3,           # MySQL应用错误
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}': 3,  # 应用日志时间戳
        r'INFO|WARN|ERROR|DEBUG:': 3,      # 应用日志级别标识
    }
    # 连续日志的开头标志及其后续行判断依据
    mandatory = {
        # 内核最核心栈头，后续是完整调用栈帧
        r'Call Trace:': [
            r'\+[0-9a-fx]+/[0-9a-fx]+',  # 模块符号+偏移/总长度
            r'\[[a-zA-Z0-9_]+\]\s*$',     # 行尾模块名标识
            r'</?(IRQ|NMI|SOFTIRQ|HARDIRQ)>',  # 中断上下文标记
            r'^\s+',                      # 栈帧缩进行
            r'^\? ',                      # 符号解析失败的?开头行
            r'\[\<[0-9a-fA-F]+\>\]',      # x86架构地址[<xxxx>]格式
            r'pc : \w+',                  # ARM/ARM64 PC寄存器行
            r'lr : \w+',                  # ARM/ARM64 LR寄存器行
            r'\s+[0-9a-fx]+\s+',          # 栈地址/偏移数值
        ],
        # 嵌入式/ARM架构通用回溯头，后续行同Call Trace
        r'Backtrace:\s*$': [
            r'\+[0-9a-fx]+/[0-9a-fx]+',
            r'\[[a-zA-Z0-9_]+\]\s*$',
            r'^\s+',
            r'^\? ',
            r'pc : \w+',
            r'lr : \w+',
        ],
        # 内核Oops轻崩溃头，后续紧跟Call Trace及栈帧
        r'Oops: \w+, \[\#\d+\]': [
            r'CPU: \d+ PID: \d+ Comm: \w+',  # 崩溃CPU/PID/进程信息
            r'Call Trace:',                # 后续关联核心栈头
            r'pc is at \w+\+0x[0-9a-fx]+',  # 故障PC地址
            r'lr is at \w+\+0x[0-9a-fx]+',  # 故障LR地址
        ],
        # 内核panic致命崩溃头，后续是故障信息+Call Trace
        r'panic: .+': [
            r'CPU: \d+ PID: \d+ Comm: \w+',
            r'Call Trace:',
            r'Kernel panic - not syncing:',
            r'Pid: \d+, comm: \w+',
        ],
        # KASAN内存检测崩溃头，后续是内存故障+Call Trace
        r'\+\+\+ killed by KASAN \+\+\+': [
            r'Call Trace:',
            r'^\s+',
            r'\+[0-9a-fx]+/[0-9a-fx]+',
            r'\[[a-zA-Z0-9_]+\]\s*$',
        ]
    }

    @staticmethod
    async def _check_negative_keywords(log_lines: list[str]) -> bool:
        """异步检查负向关键字，存在则返回True"""
        for negative_pattern in DMESGParser.negative_keywords.keys():
            if any(re.search(negative_pattern, line) for line in log_lines):
                return True
        return False

    @staticmethod
    async def _check_mandatory_patterns(log_lines: list[str]) -> bool:
        """异步检查mandatory核心头，匹配则返回True"""
        for mandatory_pattern, continuation_patterns in DMESGParser.mandatory.items():
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
        for positive_pattern in DMESGParser.positive_keywords.keys():
            if any(re.search(positive_pattern, line) for line in log_lines):
                return True
        return False

    @staticmethod
    async def is_matched(log_lines: list[str]) -> bool:
        """
        二次确认：精准匹配DMESG栈日志核心特征（协程并发优化版）
        规则：1. 不含负向关键字 2. 匹配至少1个mandatory头 或 正向关键字
        """
        batch_size = 100000
        # 第一步：分批次异步检查负向关键字
        nagetive_tasks = []
        for i in range(0, len(log_lines), 3*batch_size):
            batch = log_lines[i:i+3*batch_size]
            j = i
            while j < min(i+3*batch_size, len(log_lines)):
                sub_batch = batch[j, min(j+batch_size, len(batch))]
                nagetive_tasks.append(
                    DMESGParser._check_negative_keywords(sub_batch))
                j += batch_size
            nagetive_results = await asyncio.gather(*nagetive_tasks)
            for result in nagetive_results:
                if result:
                    return False  # 存在负向关键字，直接排除
        # 第二步：分批次异步检查mandatory头
        mandatory_tasks = []
        for i in range(0, len(log_lines), 3*batch_size):
            batch = log_lines[i:i+3*batch_size]
            j = i
            while j < min(i+3*batch_size, len(log_lines)):
                sub_batch = batch[j, min(j+batch_size, len(batch))]
                mandatory_tasks.append(
                    DMESGParser._check_mandatory_patterns(sub_batch))
                j += batch_size
            mandatory_results = await asyncio.gather(*mandatory_tasks)
            for result in mandatory_results:
                if result:
                    return True  # 匹配到mandatory头，直接确认
        # 第三步：分批次异步检查正向关键字
        positive_tasks = []
        for i in range(0, len(log_lines), 3*batch_size):
            batch = log_lines[i:i+3*batch_size]
            j = i
            while j < min(i+3*batch_size, len(log_lines)):
                sub_batch = batch[j, min(j+batch_size, len(batch))]
                positive_tasks.append(
                    DMESGParser._check_positive_keywords(sub_batch))
                j += batch_size
            positive_results = await asyncio.gather(*positive_tasks)
            for result in positive_results:
                if result:
                    return True  # 匹配到正向关键字，确认为DMESG日志
        return False  # 未匹配到任何特征，排除为非DMESG日志

    @staticmethod
    async def split_logs(log_lines: list[str]) -> list[LogModel]:
        results = []
        index = 0
        while index < len(log_lines):
            line = log_lines[index]
            if any(re.search(pat, line) for pat in DMESGParser.mandatory.keys()):
                # 找到mandatory头，尝试提取完整日志块
                log_block = [line]
                for mandatory_pattern, continuation_patterns in DMESGParser.mandatory.items():
                    if re.search(mandatory_pattern, line):
                        # 继续添加后续行直到不匹配continuation_patterns
                        for j in range(index + 1, len(log_lines)):
                            if any(re.search(pat, log_lines[j]) for pat in continuation_patterns):
                                log_block.append(log_lines[j])
                            elif log_lines[j].strip() == '':  # 允许空行作为日志块间隔
                                log_block.append(log_lines[j])
                            else:
                                break
                        break
                results.append(LogModel(
                    log_type=LogTypeEnum.DMESG,
                    offset=index,
                    content="\n".join(log_block)
                ))
                index += len(log_block)  # 跳过已提取的日志块
            else:
                results.append(LogModel(
                    log_type=LogTypeEnum.DMESG,
                    offset=index,
                    content=line
                ))
                index += 1
        return results
