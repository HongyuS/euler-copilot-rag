import re
import asyncio
from apps.parser.base_parser import BaseParser
from apps.enum.log import LogTypeEnum
from apps.schemas.log import LogModel


class KdumpParser(BaseParser):
    """
    Kdump日志解析器：识别并分割Linux内核崩溃转储(kdump)日志
    精准匹配kdump核心特征，排除用户态日志干扰
    """
    log_type: LogTypeEnum = LogTypeEnum.KDUMP
    prio = 90  # 优先级高于DMESG和BASH，kdump是最核心的内核崩溃日志

    # 正向关键字：匹配kdump内核崩溃日志核心特征，权重越高匹配优先级越高
    postive_keywords = {
        r'VERIFYING kdump image': 25,          # kdump镜像验证（最高权重）
        r'kdump: saving vmcore': 25,           # kdump保存vmcore文件
        r'Crash kernel initialized': 24,       # 崩溃内核初始化
        r'Panic occurred, switching back to text console': 24,  # 崩溃切换控制台
        r'vmcore-dmesg.txt': 23,               # kdump生成的dmesg文件标识
        r'REGISTER VALUES:': 22,               # 寄存器值上下文
        r'CR2: [0-9a-fA-F]+': 22,              # 页错误地址寄存器
        r'\[ *\d+\.\d+\]\s*Kernel panic - not syncing:': 21,  # 内核panic
        r'\[ *\d+\.\d+\]\s*Oops: \w+, \[\#\d+\]': 21,         # 内核Oops崩溃
        r'\[ *\d+\.\d+\]\s*Call Trace:': 20,    # 内核调用栈
        r'CPU: \d+ PID: \d+ Comm: \w+ \#\d+': 20,  # 崩溃CPU/PID/进程信息
        r'RIP: [0-9a-fA-F]+:\[<[0-9a-fA-F]+\>]': 19,  # x86 RIP寄存器
        r'RSP: [0-9a-fA-F]+:\[<[0-9a-fA-F]+\>]': 19,  # x86 RSP寄存器
        r'pc : \w+\+0x[0-9a-fx]+/0x[0-9a-fx]+': 19,   # ARM PC寄存器
        r'lr : \w+\+0x[0-9a-fx]+/0x[0-9a-fx]+': 19,   # ARM LR寄存器
        r'Process \w+ <span data-type="inline-math" data-value="cGlkOiBcZCs="></span>:': 18,      # 崩溃进程信息
        r'Segmentation fault <span data-type="inline-math" data-value="ZmF1bHQgYWRkcmVzcyBcdys="></span>': 18,  # 段错误
        r'BUG: KASAN: use-after-free in': 18,  # KASAN内存检测错误
        r'Kernel hacking configuration:': 17,  # 内核调试配置
        r'CONFIG_CRASH_DUMP=y': 17,            # kdump配置开启
        r'\+\+\+ killed by KASAN \+\+\+': 17,  # KASAN崩溃标识
        r'Backtrace:\s*$': 16,                 # 嵌入式内核回溯
        r'\[\<[0-9a-fA-F]+\>\] \w+\+0x[0-9a-fx]+': 16,  # 栈地址+符号
        r'Modules linked in:': 15,             # 加载的内核模块列表
    }

    # 负向关键字：排除非kdump日志，权重越高排除优先级越高
    negative_keywords = {
        # 用户态编程语言日志（最高权重排除）
        r'Traceback \(most recent call last\):': 20,  # Python异常
        r'Exception in thread ".*" java\.lang\.': 20,  # Java异常
        r'goroutine \d+ \[(running|sleeping|waiting)\]': 20,  # Go协程
        r'\#\d+ 0x[0-9a-fA-F]+ in \w+ at .+:\d+': 20,  # C/C++用户态崩溃
        r'PHP (Fatal|Warning|Notice) error:': 20,      # PHP错误
        r'Error: .+\n\s+at .+:\d+:\d+': 20,            # JS/Node.js错误
        # Bash脚本日志（高权重排除）
        r'^\#!/bin/(ba|k)?sh': 18,
        r'line \d+: (syntax error|command not found)': 18,
        r'^\bbash: \w+: No such file or directory': 18,
        r'^\+ \w+': 18,
        # 普通应用日志（中权重排除）
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}': 15,  # 应用日志时间戳
        r'INFO|WARN|ERROR|DEBUG:': 15,                # 应用日志级别
        r'nginx: \[error\]|mysqld: \[ERROR\]': 15,    # 应用错误
        # 普通dmesg日志（低权重排除，避免误删kdump中的dmesg片段）
        r'usb \d+-\d+: new high-speed USB device number': 10,
        r'eth0: link up': 10,
        r'EXT4-fs \(\w+\): mounted filesystem with ordered data mode': 10,
        r'IPv6: ADDRCONF(NETDEV_CHANGE)': 10,
    }

    # kdump核心日志块及其后续行判断依据
    mandatory = {
        # kdump最核心的panic头，后续是完整崩溃信息
        r'Kernel panic - not syncing:': [
            r'CPU: \d+ PID: \d+ Comm: \w+',      # 崩溃CPU/PID信息
            r'Call Trace:',                      # 调用栈起始
            r'Registers:|REGISTER VALUES:',       # 寄存器信息
            r'Process \w+ \(pid: \d+\):',        # 崩溃进程信息
            r'^\s+\[\<[0-9a-fA-F]+\>\]',         # 栈地址行
            r'Kernel Offset:|KASLR offset:',     # 内核偏移信息
        ],
        # kdump Oops崩溃头，后续是完整错误上下文
        r'Oops: \w+, \[\#\d+\]': [
            r'CPU: \d+ PID: \d+ Comm: \w+',      # 崩溃上下文
            r'RIP: |RSP: |RAX: |RBX: ',          # x86寄存器
            r'pc : |lr : |sp : ',                # ARM寄存器
            r'Call Trace:',                      # 调用栈
            r'Code: [0-9a-f ]+',                 # 出错机器码
            r'Segmentation fault|page fault',    # 错误类型
        ],
        # kdump调用栈头，后续是完整栈帧
        r'Call Trace:': [
            r'\[\<[0-9a-fA-F]+\>\] \w+\+0x[0-9a-fx]+',  # 栈地址+符号
            r'\+[0-9a-fx]+/[0-9a-fx]+ \[\w+\]',          # 模块+偏移
            r'^\s+',                                # 栈帧缩进行
            r'^\? ',                                # 符号解析失败
            r'pc : \w+\+0x[0-9a-fx]+',              # ARM栈帧
            r'lr : \w+\+0x[0-9a-fx]+',              # ARM栈帧
            r'</?(IRQ|NMI|SOFTIRQ)>',               # 中断上下文
        ],
        # kdump寄存器信息头，后续是寄存器值
        r'REGISTER VALUES:|Registers:': [
            r'R\d+ : [0-9a-fA-F]+',                 # ARM寄存器
            r'RIP: |RSP: |RAX: |RBX: |RCX: |RDX: ',  # x86寄存器
            r'CR2: [0-9a-fA-F]+',                   # 页错误地址
            r'eflags: [0-9a-fA-F]+',                # 标志寄存器
            r'cs: \d+ ss: \d+ ds: \d+ es: \d+',     # 段寄存器
        ],
        # kdump KASAN内存错误头，后续是内存故障信息
        r'BUG: KASAN: \w+ in': [
            r'Write of size \d+ at addr [0-9a-fA-F]+',  # 写错误信息
            r'Allocated by task \d+:|Freed by task \d+:',  # 内存分配/释放
            r'Call Trace:',                      # 调用栈
            r'\+\+\+ killed by KASAN \+\+\+',     # KASAN结束标识
            r'^\s+\[\<[0-9a-fA-F]+\>\]',         # 栈地址行
        ],
    }

    @staticmethod
    async def _check_negative_keywords(log_lines: list[str]) -> bool:
        """异步检查负向关键字，存在则返回True"""
        for negative_pattern in KdumpParser.negative_keywords.keys():
            if any(re.search(negative_pattern, line) for line in log_lines):
                return True
        return False

    @staticmethod
    async def _check_mandatory_patterns(log_lines: list[str]) -> bool:
        """异步检查mandatory核心头，匹配则返回True"""
        for mandatory_pattern, continuation_patterns in KdumpParser.mandatory.items():
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
        for positive_pattern in KdumpParser.positive_keywords.keys():
            if any(re.search(positive_pattern, line) for line in log_lines):
                return True
        return False

    @staticmethod
    async def is_matched(log_lines: list[str]) -> bool:
        """
        二次确认：精准匹配kdump内核崩溃日志核心特征
        规则：1. 不含负向关键字 2. 匹配至少1个mandatory头 或 正向关键字
        """
        batch_size = 100000

        # 第一步：分批次异步检查负向关键字（存在则直接排除）
        nagetive_tasks = []
        for i in range(0, len(log_lines), 3*batch_size):
            batch = log_lines[i:i+3*batch_size]
            j = 0
            while j < len(batch):
                sub_batch = batch[j:j+batch_size]
                nagetive_tasks.append(
                    KdumpParser._check_negative_keywords(sub_batch))
                j += batch_size
            nagetive_results = await asyncio.gather(*nagetive_tasks)
            if any(nagetive_results):
                return False

        # 第二步：分批次异步检查mandatory头（匹配则直接确认）
        mandatory_tasks = []
        for i in range(0, len(log_lines), 3*batch_size):
            batch = log_lines[i:i+3*batch_size]
            j = 0
            while j < len(batch):
                sub_batch = batch[j:j+batch_size]
                mandatory_tasks.append(
                    KdumpParser._check_mandatory_patterns(sub_batch))
                j += batch_size
            mandatory_results = await asyncio.gather(*mandatory_tasks)
            if any(mandatory_results):
                return True

        # 第三步：分批次异步检查正向关键字
        positive_tasks = []
        for i in range(0, len(log_lines), 3*batch_size):
            batch = log_lines[i:i+3*batch_size]
            j = 0
            while j < len(batch):
                sub_batch = batch[j:j+batch_size]
                positive_tasks.append(
                    KdumpParser._check_positive_keywords(sub_batch))
                j += batch_size
            positive_results = await asyncio.gather(*positive_tasks)
            if any(positive_results):
                return True

        return False  # 未匹配到任何kdump特征

    @staticmethod
    async def split_logs(log_lines: list[str]) -> list[LogModel]:
        """
        分割kdump日志：将完整的崩溃日志块合并，保留完整的崩溃上下文
        """
        results = []
        index = 0
        log_count = len(log_lines)

        while index < log_count:
            line = log_lines[index]
            matched_mandatory = False

            # 检查是否匹配kdump核心日志块起始
            for mandatory_pattern, continuation_patterns in KdumpParser.mandatory.items():
                if re.search(mandatory_pattern, line):
                    matched_mandatory = True
                    log_block = [line]
                    current_pos = index + 1

                    # 持续收集后续行直到不再匹配continuation_patterns
                    # 增加连续空行判断，避免过度收集
                    empty_line_count = 0
                    while current_pos < log_count and empty_line_count < 3:
                        current_line = log_lines[current_pos]

                        # 检查是否匹配续行规则
                        if any(re.search(pat, current_line) for pat in continuation_patterns):
                            log_block.append(current_line)
                            empty_line_count = 0  # 重置空行计数
                            current_pos += 1
                        elif current_line.strip() == "":
                            # 空行也加入（保留日志格式），但计数
                            log_block.append(current_line)
                            empty_line_count += 1
                            current_pos += 1
                        else:
                            break

                    # 添加完整的kdump日志块
                    results.append(LogModel(
                        log_type=LogTypeEnum.KDUMP,
                        offset=index,
                        content="\n".join(log_block)
                    ))
                    index = current_pos  # 跳过已处理的行
                    break

            # 如果不是核心日志块，单独处理单行
            if not matched_mandatory:
                results.append(LogModel(
                    log_type=LogTypeEnum.KDUMP,
                    offset=index,
                    content=line
                ))
                index += 1

        return results
