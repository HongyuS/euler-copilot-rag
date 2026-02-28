from apps.enum.log import LogTypeEnum, LogValueEnum


class DmesgLogFeature:
    """
    判断是否为当前日志的正则表达式及其对应的分数
    """
    keywords_regex_and_scores = {
        "normal":
        {
            r'localhost kernel:': 2.0,          # 经典syslog格式dmesg头（最高权重）
            r'\[ *\d+\.\d+\] \w+:': 1.8,        # dmesg标准时间戳+子系统
            r'kernel: \[ *\d+\.\d+\]': 1.8,     # 反向格式syslog
            r'\[\<[0-9a-fA-F]+\>\]': 1.6,       # x86架构栈地址格式
            r'pc : |lr : |elr_el1:': 1.6,       # ARM/ARM64架构寄存器标识
            "kernel:": 1.5,                     # 基础kernel标识
            "dmesg": 1.2,                       # dmesg关键字
            r"\b\w+\[\d+\]:": 0.8,              # 通用进程日志格式（低权重）
        },
        "anomalous":
        {
            r'\[ *\d+\.\d+\]\s*Call Trace:': 1.9,  # 带时间戳的核心栈头
            r'\[ *\d+\.\d+\]\s*Oops:': 1.9,     # 带时间戳的Oops崩溃
            r'\[ *\d+\.\d+\]\s*panic:': 1.9,    # 带时间戳的panic崩溃
            r'CPU: \d+ PID: \d+ Comm:': 1.7,    # dmesg崩溃核心上下文
            r'Backtrace:\s*$': 1.7,             # 嵌入式内核回溯头
            r'\+\+\+ killed by KASAN \+\+\+': 1.7,  # KASAN内存检测崩溃标识
        }
    }

    """
    判断是否为连续多行日志的启示头以及后续跟连续行的正则表达式
    """
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
        # 嵌入式/ARM架构通用回溯头
        r'Backtrace:\s*$': [
            r'\+[0-9a-fx]+/[0-9a-fx]+',
            r'\[[a-zA-Z0-9_]+\]\s*$',
            r'^\s+',
            r'^\? ',
            r'pc : \w+',
            r'lr : \w+',
        ],
        # 内核Oops轻崩溃头
        r'Oops: \w+, \[\#\d+\]': [
            r'CPU: \d+ PID: \d+ Comm: \w+',  # 崩溃CPU/PID/进程信息
            r'Call Trace:',                # 后续关联核心栈头
            r'pc is at \w+\+0x[0-9a-fx]+',  # 故障PC地址
            r'lr is at \w+\+0x[0-9a-fx]+',  # 故障LR地址
        ],
        # 内核panic致命崩溃头
        r'panic: .+': [
            r'CPU: \d+ PID: \d+ Comm: \w+',
            r'Call Trace:',
            r'Kernel panic - not syncing:',
            r'Pid: \d+, comm: \w+',
        ],
        # KASAN内存检测崩溃头
        r'\+\+\+ killed by KASAN \+\+\+': [
            r'Call Trace:',
            r'^\s+',
            r'\+[0-9a-fx]+/[0-9a-fx]+',
            r'\[[a-zA-Z0-9_]+\]\s*$',
        ],
        "kernel:": [
            r"\[\s*\d+\.\d+\]",  # 匹配类似于 "[12345.678901]" 的时间戳
            r"error|warn|fail|critical|trace|unknown|fatal",  # 匹配日志级别
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",  # 匹配IP地址
            r"\b\d{1,5}\b",  # 匹配端口号
            r"\bPID[:=]?\s*\d+\b",  # 匹配PID
            r"\bTID[:=]?\s*\d+\b",  # 匹配TID
        ]
    }

    """
    捕获各种数值的正则表达式
     - timestamp: 时间戳
     - level: 日志级别
     - ip: IP地址
     - port: 端口号
     - pid: 进程ID
     - tid: 线程ID
    """
    capture_patterns = {
        # 兼容dmesg特有时间戳
        LogValueEnum.TIMESTAMP: r"\b(?:\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|\[\s*\d+\.\d+\])\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL|Oops|panic)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        LogValueEnum.PID: r"\b(?:PID|Comm:)\s*\d+\b",  # 兼容dmesg的Comm格式
        LogValueEnum.TID: r"\bTID[:=]?\s*\d+\b"
    }


class KdumpLogFeature:
    """
    Kdump内核崩溃日志特征
    """
    keywords_regex_and_scores = {
        "normal": {
            r'Kdump:': 2.0,                     # Kdump标识头（最高权重）
            r'vmcore': 1.9,                     # 崩溃内存镜像文件
            r'crash>': 1.8,                     # crash工具交互提示符
            r'kdump': 1.5,                      # kdump关键字
            r'core dump': 1.4,                  # 核心转储通用标识
        },
        "anomalous": {
            r'PANIC: ': 1.8,                    # 内核panic标识
            r'Vmlinux Path:': 1.7,              # 内核镜像路径
            r'bt\s+#\d+': 1.7,                  # crash工具回溯命令输出
            r'PID: \d+ \(comm: \w+\)': 1.7,     # 崩溃进程信息
            r'RIP: |RSP: |RAX: ': 1.6,          # x86寄存器信息
            r'Segmentation fault': 1.6,         # 段错误
            r'Kernel panic - not syncing:': 1.6,  # 内核panic详情
        }
    }

    mandatory = {
        # Kdump核心回溯头
        r'crash> bt': [
            r'#\d+\s+[0-9a-fx]+\s+',        # 栈帧编号+地址
            r'in \w+ at .+:\d+',            # 函数+文件行号
            r'^\s+',                        # 缩进的栈帧行
            r'RIP: [0-9a-fx]+',             # 指令指针
            r'RSP: [0-9a-fx]+',             # 栈指针
        ],
        # PANIC崩溃头
        r'PANIC: .+': [
            r'CPU: \d+ PID: \d+',           # CPU/PID信息
            r'Call Trace:',                 # 调用栈
            r'kernel \[\#\d+\]',            # 内核版本
            r'^\s+',                        # 缩进行
        ],
        r'vmcore': [
            r'ELF64|ELF32',                 # 核心文件格式
            r'x86_64|arm64|aarch64',        # 架构信息
            r'crash tool',                  # crash工具标识
            r'gdb:',                        # gdb调试标识
        ]
    }

    capture_patterns = {
        LogValueEnum.TIMESTAMP: r"\b(?:\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|\[\s*\d+\.\d+\])\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL|PANIC|panic)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        LogValueEnum.PID: r"\bPID[:=]?\s*\d+\b",
        LogValueEnum.TID: r"\bTID[:=]?\s*\d+\b"
    }


class FtraceLogFeature:
    """
    Ftrace内核跟踪日志特征
    """
    keywords_regex_and_scores = {
        "normal": {
            r'# tracer:': 2.0,                  # Ftrace跟踪器标识
            r'ftrace:': 1.9,                    # ftrace关键字头
            r'^[\|\-]+ ': 1.8,                  # Ftrace函数调用图符号
            r'function_graph:': 1.8,           # 函数图跟踪器
            r'^[\d\.]+\s+\d+\s+\d+\s+': 1.7,    # Ftrace时间戳+PID+CPU格式
            r'^<idle>-0\s+': 1.7,               # 空闲进程跟踪
            r'^swapper/\d+-\d+\s+': 1.7,        # 交换进程跟踪
            r'ftrace': 1.5,                     # ftrace关键字
        },
        "anomalous": {
            r'latency_top:': 1.6,               # 延迟跟踪（异常指标）
            r'irqsoff:': 1.6,                   # 中断关闭跟踪（异常指标）
            r'preemptoff:': 1.6,                # 抢占关闭跟踪（异常指标）
        }
    }

    mandatory = {
        # 函数图跟踪器头
        r'function_graph:': [
            r'^[\|\-]+ \w+\+0x[0-9a-f]+',   # 函数调用图+偏移
            r'^[\|\-]+ \w+\(\)',             # 函数调用
            r'^\s*\d+us\s+',                # 耗时统计
            r'^\+ \d+\.\d+us',              # 函数执行时间
            r'^[\|\-]+$',                   # 调用图结束符
        ],
        # Ftrace跟踪器配置头
        r'# tracer:': [
            r'#\s+entries:\s+\d+',          # 条目数
            r'#\s+buf_size:\s+\d+',         # 缓冲区大小
            r'#\s+CPU:\s+\d+',              # CPU编号
            r'#\s+print-parent:\s+\w+',     # 打印父函数
            r'^#\s+\w+:\s+.+',              # 配置项
        ],
        r'ftrace:': [
            r"^\d+\.\d+\s+\d+\s+\d+\s+",    # Ftrace时间戳+PID+CPU
            r"\bCPU[:=]?\s*\d+\b",          # CPU编号
            r"\bPID[:=]?\s*\d+\b",          # PID
            r"\bus\b|\bms\b|\bs\b",         # 时间单位
        ]
    }

    capture_patterns = {
        # 兼容ftrace时间戳
        LogValueEnum.TIMESTAMP: r"\b(?:\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|\d+\.\d+)\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        # 兼容ftrace的PID位置
        LogValueEnum.PID: r"\bPID[:=]?\s*\d+|\b\d+\s+\d+\s+\w+",
        LogValueEnum.TID: r"\bTID[:=]?\s*\d+\b"
    }


class BashLogFeature:
    """
    Bash脚本日志特征
    """
    keywords_regex_and_scores = {
        "normal": {
            r'^\#!/bin/(ba|k)?sh': 2.0,         # Shebang标识（最高权重）
            r'^set -[xe]': 1.8,                 # Shell调试模式
            r'^\+ \w+': 1.8,                    # Shell执行跟踪
            r'bash': 1.5,                       # bash关键字
            r'sh': 1.4,                         # sh关键字
            r'shell': 1.3,                      # shell关键字
        },
        "anomalous": {
            # 脚本错误
            r'line \d+: (syntax error|command not found|unbound variable)': 1.9,
            r'\bbash: \w+: No such file or directory': 1.8,  # 文件不存在
            r'\bsh: \d+: \w+: not found': 1.8,  # 命令未找到
            r'\bbash: .+: Permission denied': 1.8,  # 权限拒绝
            r'\/bin\/sh: .+ not found': 1.8,    # Shell命令未找到
            r'segmentation fault \(core dumped\)': 1.7,  # 段错误
        }
    }

    mandatory = {
        # Shell错误行
        r'line \d+:': [
            r'syntax error near unexpected token',  # 语法错误
            r'command substitution: line \d+:',  # 命令替换错误
            r'^\s+',                              # 缩进的错误详情
            r'\`\w+\'',                           # 出错的命令
            r'No such file or directory',         # 文件不存在
        ],
        # Shebang头
        r'^\#!/bin/(ba|k)?sh': [
            r'^#',                              # 注释行
            r'^export \w+=',                    # 环境变量设置
            r'^alias \w+=',                     # 别名设置
            r'^function \w+',                   # 函数定义
            r'^\w+\(\) \{',                     # 函数声明
        ],
        # Shell调试输出
        r'^\+ \w+': [
            r'^\+ \w+',                         # 连续的执行跟踪行
            r'^\+\[\[',                         # 条件判断
            r'^\+if |^\+for |^\+while',         # 循环/条件语句
            r'^\+echo |^\+printf',              # 输出命令
        ]
    }

    capture_patterns = {
        LogValueEnum.TIMESTAMP: r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL|syntax error|Permission denied)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        LogValueEnum.PID: r"\bPID[:=]?\s*\d+\b",
        LogValueEnum.TID: r"\bTID[:=]?\s*\d+\b"
    }


class PythonLogFeature:
    """
    Python日志特征
    """
    keywords_regex_and_scores = {
        "normal": {
            r'^>>> ': 1.7,                                 # Python交互提示符
            r'python': 1.6,                                # python关键字
            r'py:': 1.5,                                   # py后缀标识
            r'import |from ': 1.4,                         # 导入语句
            r'def \w+': 1.4,                               # 函数定义
        },
        "anomalous": {
            r'Traceback <span data-type="inline-math" data-value="bW9zdCByZWNlbnQgY2FsbCBsYXN0"></span>:': 2.0,  # Python回溯头（最高权重）
            r'File ".+", line \d+, in \w+': 1.9,           # 文件行号信息
            # 函数调用行
            r'^\s+(\w+\.)*\w+(<span data-type="inline-math" data-value="Lio="></span>)?': 1.8,
            r'(\w+)Error: ': 1.8,                          # 各类Python异常
            r'Exception in thread': 1.8,                   # 线程异常
        }
    }

    mandatory = {        # Python回溯头
        r'Traceback <span data-type="inline-math" data-value="bW9zdCByZWNlbnQgY2FsbCBsYXN0"></span>:': [
            r'File ".+", line \d+, in \w+',  # 文件行号信息
            # 函数调用行
            r'^\s+(\w+\.)*\w+(<span data-type="inline-math" data-value="Lio="></span>)?',
            r'(\w+)Error: .+',              # 异常类型+描述
            r'^\s+',                        # 缩进的回溯行
            r'AttributeError|TypeError|ValueError|KeyError|IndexError',  # 常见异常
        ],
        # Python线程异常
        r'Exception in thread': [
            r'Traceback <span data-type="inline-math" data-value="bW9zdCByZWNlbnQgY2FsbCBsYXN0"></span>:',  # 关联回溯
            r'File ".+", line \d+, in \w+',           # 文件行号
            r'(\w+)Error: .+',                        # 异常信息
        ],
        r'python': [
            r"\b\d+\.\d+\.\d+\b",           # Python版本号
            r"module '(\w+)' has no attribute",  # 模块属性错误
            r"no module named '(\w+)'",    # 模块未找到
            r"SyntaxError:",               # 语法错误
        ]
    }

    capture_patterns = {
        LogValueEnum.TIMESTAMP: r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL|(\w+)Error)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        LogValueEnum.PID: r"\bPID[:=]?\s*\d+\b",
        LogValueEnum.TID: r"\b(?:TID|thread)\s*\d+\b"  # 兼容thread关键字
    }


class JavaLogFeature:
    """
    Java日志特征
    """
    keywords_regex_and_scores = {
        "normal": {
            r'java.lang.': 1.8,                            # Java核心包
            r'javax.': 1.7,                                # Java扩展包
            r'org.springframework.': 1.7,                  # Spring框架
            r'com.': 1.7,                                  # 企业包名前缀
            r'java': 1.6,                                  # java关键字
            r'jvm': 1.6,                                   # JVM标识
        },
        "anomalous": {
            r'Exception in thread': 2.0,                # Java线程异常（最高权重）
            r'(\w+)Exception: ': 1.9,                      # Java异常类型
            # 堆栈跟踪行
            r'at (\w+\.)+\w+<span data-type="inline-math" data-value="Lis6XGQr"></span>': 1.9,
            r'Caused by: ': 1.8,                           # 异常原因
            r'class file for .+ not found': 1.5,           # 类未找到
        }
    }

    mandatory = {        # Java异常头
        r'Exception in thread': [
            # 堆栈跟踪行
            r'at (\w+\.)+\w+<span data-type="inline-math" data-value="Lis6XGQr"></span>',
            r'Caused by: ',               # 异常原因
            r'(\w+)Exception: .+',        # 异常描述
            r'^\s+',                      # 缩进的堆栈行
            r'java.lang.(\w+)Exception',  # 核心异常类型
        ],
        # 异常原因
        r'Caused by: ': [
            # 堆栈跟踪行
            r'at (\w+\.)+\w+<span data-type="inline-math" data-value="Lis6XGQr"></span>',
            r'(\w+)Exception: .+',        # 异常描述
            r'^\s+',                      # 缩进行
            r'Also caused by: ',          # 多重原因
        ],
        r'java': [
            r"\b\d+\.\d+\.\d+\b",         # Java版本号
            r"OutOfMemoryError",          # 内存溢出
            r"NullPointerException",      # 空指针异常
            r"ClassNotFoundException",    # 类未找到
        ]
    }

    capture_patterns = {
        LogValueEnum.TIMESTAMP: r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL|(\w+)Exception)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        LogValueEnum.PID: r"\bPID[:=]?\s*\d+\b",
        LogValueEnum.TID: r"\b(?:TID|thread)\s*\d+\b"
    }


class GoLogFeature:
    """
    Go语言日志特征
    """
    keywords_regex_and_scores = {
        "normal": {
            r'go': 1.7,                                          # go关键字
            r'Golang': 1.7,                                      # Golang标识
            r'go routine': 1.6,                                  # 协程描述
        },
        "anomalous": {
            # Go协程（最高权重）
            r'goroutine \d+ \[(running|sleeping|waiting)': 2.0,
            r'^goroutine \d+:$': 1.9,                            # 协程头
            r'created by (\w+\.)+\w+ in .+:\d+': 1.9,            # 协程创建信息
            r'at (\w+\.)+\w+(.+:\d+)': 1.8,                      # 堆栈行
            r'panic: ': 1.8,                                     # Go panic
            r'runtime error: ': 1.8,                             # 运行时错误
            r'interface conversion: ': 1.6,                      # 接口转换错误
        }
    }

    mandatory = {        # Go协程头
        r'goroutine \d+ ': [
            r'^\s+at (\w+\.)+\w+(.+:\d+)',  # 堆栈行
            r'^\s+created by (\w+\.)+\w+',  # 创建信息
            r'^\s+',                        # 缩进的堆栈行
            r'<span data-type="inline-math" data-value="Lio="></span>$',                     # 函数参数
        ],
        # Go Panic
        r'panic: ': [
            r'goroutine \d+ ',              # 关联协程
            r'runtime error: ',             # 运行时错误
            r'at (\w+\.)+\w+(.+:\d+)',      # 堆栈行
            r'^\s+',                        # 缩进行
        ],
        r'go': [
            r"\b\d+\.\d+\.\d+\b",           # Go版本号
            r"deadlock",                    # 死锁
            r"nil pointer dereference",     # 空指针解引用
            r"index out of range",          # 索引越界
        ]
    }

    capture_patterns = {
        LogValueEnum.TIMESTAMP: r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL|panic|runtime error)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        LogValueEnum.PID: r"\bPID[:=]?\s*\d+\b",
        LogValueEnum.TID: r"\b(?:TID|goroutine)\s*\d+\b"  # 兼容goroutine
    }


class JsLogFeature:
    """
    JavaScript/Node.js日志特征
    """
    keywords_regex_and_scores = {
        "normal": {
            r'javascript': 1.7,                   # javascript关键字
            r'js': 1.7,                           # js关键字
            r'node': 1.6,                         # node.js标识
            r'v8:': 1.6,                          # V8引擎标识
        },
        "anomalous": {
            r'Error: .+\n\s+at .+:\d+:\d+': 2.0,  # JS错误栈（最高权重）
            r'Uncaught (\w+)Error: ': 1.9,        # 未捕获异常
            # 堆栈跟踪行
            r'^\s+at (\w+ )?<span data-type="inline-math" data-value="Lis6XGQrOlxkKw=="></span>': 1.9,
            r'ReferenceError: ': 1.8,             # 引用错误
            r'TypeError: ': 1.8,                  # 类型错误
            r'SyntaxError: ': 1.8,                # 语法错误
        }
    }

    mandatory = {        # JS错误头
        r'Error: ': [
            # 堆栈行
            r'^\s+at (\w+ )?<span data-type="inline-math" data-value="Lis6XGQrOlxkKw=="></span>',
            r'Uncaught ',                     # 未捕获标记
            r'^\s+',                          # 缩进的堆栈行
            r'<span data-type="inline-math" data-value="Lis6XGQrOlxkKw=="></span>',                # 文件位置
        ],
        # Node.js错误
        r'node:': [
            # 堆栈行
            r'^\s+at (\w+ )?<span data-type="inline-math" data-value="Lis6XGQrOlxkKw=="></span>',
            r'Error: |(\w+)Error:',           # 错误类型
            r'^\s+',                          # 缩进行
        ],
        r'js': [
            r"\b\d+\.\d+\.\d+\b",             # Node版本号
            r"require<span data-type=\"inline-math\" data-value=\"Jy4rJw == \"></span>",  # 模块导入
            r"module\.exports",               # 模块导出
            r"import |export ",               # ES6模块
        ]
    }

    capture_patterns = {
        LogValueEnum.TIMESTAMP: r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL|(\w+)Error)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        LogValueEnum.PID: r"\bPID[:=]?\s*\d+\b",
        LogValueEnum.TID: r"\bTID[:=]?\s*\d+\b"
    }


class CLogFeature:
    """
    C语言日志特征
    """
    keywords_regex_and_scores = {
        "normal": {
            r'c:': 1.7,                                     # .c文件后缀
            r'gcc': 1.7,                                     # GCC编译器
            r'clang': 1.7,                                   # Clang编译器
        },
        "anomalous": {
            r'\#\d+ 0x[0-9a-fA-F]+ in \w+ at .+:\d+': 2.0,  # C堆栈行（最高权重）
            r'Segmentation fault <span data-type="inline-math" data-value="Y29yZSBkdW1wZWQ="></span>': 1.9,     # 段错误
            r'Aborted <span data-type="inline-math" data-value="Y29yZSBkdW1wZWQ="></span>': 1.9,  # 中止错误
            r'(\w+)\.c:\d+: \w+: ': 1.8,                    # C文件错误
            r'undefined reference to `\w+\'': 1.8,          # 未定义引用
            r'implicit declaration of function': 1.8,       # 函数隐式声明
            r'segfault': 1.6,                                # 段错误简写
        }
    }

    mandatory = {        # C堆栈跟踪
        r'\#\d+ 0x[0-9a-fA-F]+': [
            r'in \w+ at .+:\d+',              # 函数+文件行号
            r'from .+:\d+',                   # 调用来源
            r'^\s+',                          # 缩进的堆栈行
            # 未知函数
            r'0x[0-9a-fA-F]+ in \? <span data-type="inline-math" data-value="IA=="></span> ',
        ],
        # 编译错误
        r'(\w+)\.c:\d+:': [
            r'\w+: .+',                       # 错误类型+描述
            r'warning: .+',                   # 警告信息
            r'note: .+',                      # 备注信息
            r'^\s+',                          # 缩进行
        ],
        r'c': [
            r"\b\d+\.\d+\.\d+\b",             # GCC版本号
            r"null pointer dereference",     # 空指针解引用
            r"buffer overflow",              # 缓冲区溢出
            r"stack overflow",               # 栈溢出
        ]
    }

    capture_patterns = {
        LogValueEnum.TIMESTAMP: r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL|error|warning|note)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        LogValueEnum.PID: r"\bPID[:=]?\s*\d+\b",
        LogValueEnum.TID: r"\bTID[:=]?\s*\d+\b"
    }


class CppLogFeature:
    """
    C++语言日志特征
    """
    keywords_regex_and_scores = {
        "normal": {
            r'cpp:': 1.8,                                           # .cpp文件后缀
            r'c\+\+': 1.7,                                          # c++关键字
            r'g\+\+': 1.7,                                          # G++编译器
        },
        "anomalous": {
            r'\#\d+ 0x[0-9a-fA-F]+ in (\w+::)+\w+ at .+:\d+': 2.0,  # C++堆栈行
            r'(\w+)\.cpp:\d+: \w+: ': 1.9,                         # C++文件错误
            r'undefined reference to `(\w+::)+\w+\'': 1.9,          # 未定义引用
            r'no matching function for call to `\w+\'': 1.8,        # 函数调用不匹配
            r'class `\w+\' has no member named `\w+\'': 1.8,       # 类成员不存在
            r'template argument deduction failed': 1.7,             # 模板参数推导失败
        }
    }

    mandatory = {        # C++堆栈跟踪
        r'\#\d+ 0x[0-9a-fA-F]+': [
            r'in (\w+::)+\w+ at .+:\d+',      # 命名空间+函数+文件
            r'from .+:\d+',                   # 调用来源
            r'^\s+',                          # 缩进的堆栈行
            # 类成员函数
            r'(\w+::)+\w+<span data-type="inline-math" data-value=""></span>',
        ],
        # C++编译错误
        r'(\w+)\.cpp:\d+:': [
            r'\w+: .+',                       # 错误类型+描述
            r'warning: .+',                   # 警告信息
            r'note: .+',                      # 备注信息
            r'^\s+',                          # 缩进行
        ],
        r'cpp': [
            r"\b\d+\.\d+\.\d+\b",             # G++版本号
            r"pure virtual method called",   # 纯虚函数调用
            r"bad_cast",                      # 类型转换错误
            r"out_of_range",                  # 越界错误
        ]
    }

    capture_patterns = {
        LogValueEnum.TIMESTAMP: r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL|error|warning|note)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        LogValueEnum.PID: r"\bPID[:=]?\s*\d+\b",
        LogValueEnum.TID: r"\bTID[:=]?\s*\d+\b"
    }


class UnKnownLogFeature:
    """
    其他类型日志特征（兜底）
    """
    keywords_regex_and_scores = {
        "normal": {
            r'^\w+ \[\d+\]:': 1.0,                # 通用进程日志格式
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}': 0.9,  # 通用时间戳
            r'INFO:': 0.8,                        # INFO级别
            r'\[INFO\]': 0.8,                     # 括号包裹的INFO级别
            r'^LOG:': 0.7,                       # LOG前缀
        },
        "anomalous": {
            r'WARN|ERROR|DEBUG:': 0.8,           # 警告/错误/调试级别
            r'\[ERROR\]|\[WARN\]': 0.8,          # 括号包裹的错误/警告级别
            r'^WARNING:': 0.7,                   # WARNING前缀
            r'^ERROR:': 0.7,                     # ERROR前缀
        }
    }

    mandatory = {
        # 通用日志头
        r'^\d{4}-\d{2}-\d{2}': [
            r"\d{2}:\d{2}:\d{2}",             # 时间戳后半部分
            r"\b(DEBUG|INFO|WARNING|ERROR)\b",  # 日志级别
            r"^\s+",                          # 缩进的日志内容
            r"\|\s+\w+",                      # 分隔符+内容
        ],
        # 通用级别头
        r'INFO|WARN|ERROR|DEBUG:': [
            r"^\s+",                          # 缩进的内容
            r"\b\w+\b",                       # 任意单词
            r"\d+",                           # 任意数字
        ]
    }

    capture_patterns = {
        LogValueEnum.TIMESTAMP: r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\b",
        LogValueEnum.LEVEL: r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL|TRACE|UNKNOWN|FATAL)\b",
        LogValueEnum.IP: r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        LogValueEnum.PORT: r"\b\d{1,5}\b",
        LogValueEnum.PID: r"\bPID[:=]?\s*\d+\b",
        LogValueEnum.TID: r"\bTID[:=]?\s*\d+\b"
    }


# 完善日志类型到特征类的映射
log_feature_class_mapping = {
    LogTypeEnum.DMESG: DmesgLogFeature,
    LogTypeEnum.KDUMP: KdumpLogFeature,
    LogTypeEnum.FTRACE: FtraceLogFeature,
    LogTypeEnum.BASH: BashLogFeature,
    LogTypeEnum.PYTHON: PythonLogFeature,
    LogTypeEnum.JAVA: JavaLogFeature,
    LogTypeEnum.GO: GoLogFeature,
    LogTypeEnum.JS: JsLogFeature,
    LogTypeEnum.C: CLogFeature,
    LogTypeEnum.CPP: CppLogFeature,
    LogTypeEnum.UNKNOWN: UnKnownLogFeature,
}
