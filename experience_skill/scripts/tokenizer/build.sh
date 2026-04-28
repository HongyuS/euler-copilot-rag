#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/simple-src"
BUILD_DIR="${SRC_DIR}/build"
OUTPUT_DIR="${SRC_DIR}/output"
LIBSIMPLE_LINK="${SCRIPT_DIR}/libsimple"

if [[ ! -d "${SRC_DIR}" ]]; then
    echo "[ERROR] 源码目录不存在: ${SRC_DIR}"
    echo "        请确保 tokenizer/simple-src/ 下已放置 wangfenjin/simple 项目源码。"
    exit 1
fi

echo "[Tokenizer] 开始编译 simple 分词器扩展..."

# 清理旧构建缓存，防止 CMakeCache 路径冲突
if [[ -d "${BUILD_DIR}" ]]; then
    rm -rf "${BUILD_DIR}"
fi
mkdir -p "${BUILD_DIR}"

# cmake
echo "[Tokenizer] cmake..."
cmake -S "${SRC_DIR}" -B "${BUILD_DIR}" \
    -DSIMPLE_WITH_JIEBA=OFF \
    -DCMAKE_INSTALL_PREFIX="${OUTPUT_DIR}" \
    -DCMAKE_BUILD_TYPE=Release

# make
echo "[Tokenizer] make..."
make -C "${BUILD_DIR}" -j"$(nproc 2>/dev/null || echo 2)"

# install
echo "[Tokenizer] make install..."
make -C "${BUILD_DIR}" install

# 创建软链
COMPILED="${OUTPUT_DIR}/bin/libsimple.so"
if [[ ! -f "${COMPILED}" ]]; then
    echo "[ERROR] 编译后未找到 ${COMPILED}"
    exit 1
fi

if [[ -L "${LIBSIMPLE_LINK}" ]] || [[ -e "${LIBSIMPLE_LINK}" ]]; then
    rm -f "${LIBSIMPLE_LINK}"
fi
ln -s "${COMPILED}" "${LIBSIMPLE_LINK}"

echo "[Tokenizer] 编译完成: ${COMPILED} -> ${LIBSIMPLE_LINK}"
