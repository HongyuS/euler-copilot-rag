#!/bin/bash
# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
# 测试运行脚本

set -e

cd "$(dirname "$0")"

echo "================================"
echo "Data Chain 测试套件"
echo "================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Python
if ! command -v python3 &> /dev/null; then
    print_error "未找到 Python3，请安装 Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_info "Python 版本: $PYTHON_VERSION"

# 检查 pytest
if ! python3 -c "import pytest" 2>/dev/null; then
    print_warn "未安装 pytest，正在安装..."
    pip install pytest pytest-asyncio
fi

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  all         运行所有测试（默认）"
    echo "  quick       运行快速测试（排除慢测试）"
    echo "  parser      只运行解析器测试"
    echo "  rag         只运行 RAG 测试"
    echo "  performance 只运行性能测试"
    echo "  accuracy    只运行准确率测试"
    echo "  stability   只运行稳定性测试"
    echo "  coverage    运行测试并生成覆盖率报告"
    echo "  help        显示此帮助"
    echo ""
}

# 运行测试
run_tests() {
    local pytest_args="$1"
    
    print_info "运行测试..."
    print_info "参数: $pytest_args"
    echo ""
    
    if python3 -m pytest $pytest_args; then
        echo ""
        print_info "所有测试通过！"
        return 0
    else
        echo ""
        print_error "部分测试失败！"
        return 1
    fi
}

# 主逻辑
case "${1:-all}" in
    all)
        print_info "运行所有测试..."
        run_tests "-v"
        ;;
    quick)
        print_info "运行快速测试（排除慢测试）..."
        run_tests "-v -m 'not slow'"
        ;;
    parser)
        print_info "运行解析器测试..."
        run_tests "-v parser/"
        ;;
    rag)
        print_info "运行 RAG 测试..."
        run_tests "-v rag/"
        ;;
    performance)
        print_info "运行性能测试..."
        run_tests "-v -m 'performance'"
        ;;
    accuracy)
        print_info "运行准确率测试..."
        run_tests "-v -m 'accuracy'"
        ;;
    stability)
        print_info "运行稳定性测试..."
        run_tests "-v -m 'stability'"
        ;;
    coverage)
        print_info "运行测试并生成覆盖率报告..."
        pip install pytest-cov --quiet 2>/dev/null || true
        run_tests "-v --cov=data_chain --cov-report=html --cov-report=term"
        print_info "覆盖率报告已生成: htmlcov/index.html"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "未知选项: $1"
        show_help
        exit 1
        ;;
esac
