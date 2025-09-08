import argparse
import asyncio
import pandas as pd

from token_tool import TokenTool
from pydantic import BaseModel, Field


class TestEntity(BaseModel):
    """测试实体模型"""
    question: str = Field(default="", description="问题")
    answer: str = Field(default="", description="答案")
    chunk: str = Field(default="", description="上下文片段")
    llm_answer: str = Field(default="", description="大模型答案")
    related_chunk: str = Field(default="", description="相关上下文片段")
    pre: float = Field(default=0.0, description="准确率")
    rec: float = Field(default=0.0, description="召回率")
    fai: float = Field(default=0.0, description="可信度")
    rel: float = Field(default=0.0, description="相关性")
    lcs: float = Field(default=0.0, description="最长公共子串")
    leve: float = Field(default=0.0, description="编辑距离")
    jac: float = Field(default=0.0, description="Jaccard相似度")


async def read_data_from_file(input_xlsx_file: str) -> list[TestEntity]:
    """从文件读取测试数据"""
    df = pd.read_excel(input_xlsx_file)
    data = []
    for _, row in df.iterrows():
        entity = TestEntity(
            question=row.get('question', ''),
            answer=row.get('answer', ''),
            chunk=row.get('chunk', ''),
            llm_answer=row.get('llm_answer', ''),
            related_chunk=row.get('related_chunk', '')
        )
        data.append(entity)
    return data


async def write_data_to_file(output_xlsx_file: str, data: list[TestEntity]) -> None:
    """
    将测试数据写入文件
    第一个sheet写入平均分，第二个sheet写入详细数据
    """
    average_data = {
        'pre': sum(item.pre for item in data) / len(data) if data else 0,
        'rec': sum(item.rec for item in data) / len(data) if data else 0,
        'fai': sum(item.fai for item in data) / len(data) if data else 0,
        'rel': sum(item.rel for item in data) / len(data) if data else 0,
        'lcs': sum(item.lcs for item in data) / len(data) if data else 0,
        'leve': sum(item.leve for item in data) / len(data) if data else 0,
        'jac': sum(item.jac for item in data) / len(data) if data else 0,
    }
    average_df = pd.DataFrame([average_data])
    detailed_df = pd.DataFrame([item.model_dump() for item in data])
    with pd.ExcelWriter(output_xlsx_file) as writer:
        average_df.to_excel(writer, sheet_name='average', index=False)
        detailed_df.to_excel(writer, sheet_name='detailed', index=False)


async def evaluate_metrics(data: list[TestEntity], language: str) -> None:
    """评估测试数据的各项指标"""
    token_tool = TokenTool()
    for item in data:
        item.pre = await token_tool.cal_precision(item.question, item.llm_answer, language)
        item.rec = await token_tool.cal_recall(item.question, item.related_chunk, language)
        item.fai = await token_tool.cal_faithfulness(item.question, item.llm_answer, item.related_chunk, language)
        item.rel = await token_tool.cal_relevance(item.question, item.llm_answer, language)
        item.lcs = token_tool.cal_lcs(item.answer, item.llm_answer)
        item.leve = token_tool.cal_leve(item.answer, item.llm_answer)
        item.jac = token_tool.cal_jac(item.answer, item.llm_answer)
        print(f"评估完成: 问题: {item.question}, 准确率: {item.pre}, 召回率: {item.rec}, 可信度: {item.fai}, 相关性: {item.rel}, 最长公共子串: {item.lcs}, 编辑距离: {item.leve}, Jaccard相似度: {item.jac}")


def work(input_xlsx_file: str, output_xlsx_file: str, language: str) -> None:
    data = asyncio.run(read_data_from_file(input_xlsx_file))
    asyncio.run(evaluate_metrics(data, language))
    asyncio.run(write_data_to_file(output_xlsx_file, data))


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--input_xlsx_file', type=str, required=True, help='输入xlsx文件路径')
    args.add_argument('--output_xlsx_file', type=str, required=True, help='输出xlsx文件路径')
    args.add_argument('--language', type=str, default='中文', help='语言类型，默认中文zh，英文en')
    parsed_args = args.parse_args()
    work(parsed_args.input_xlsx_file, parsed_args.output_xlsx_file, parsed_args.language)
