"""
Excel 文件解析器
支持 .xlsx, .xls, .csv 格式
"""
import logging
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


class XlsxParser:
    """Excel 文档解析器"""
    
    @staticmethod
    def _extract_table_to_array(table: pd.DataFrame) -> list:
        """提取表格为数组"""
        table_array = []
        for index, row in table.iterrows():
            row_data = [str(cell) for cell in row]
            table_array.append(row_data)
        return table_array
    
    @staticmethod
    async def _read_data_from_excel(file_path: str):
        """读取 Excel 文件数据"""
        data = None
        try:
            data = pd.read_excel(file_path, sheet_name=None, header=None, engine='openpyxl')
        except Exception as e:
            logger.warning(f"[XlsxParser] 使用 openpyxl 引擎失败: {e}")
        
        if data:
            return data
        
        try:
            data = pd.read_excel(file_path, sheet_name=None, header=None, engine='xlrd')
        except Exception as e:
            logger.warning(f"[XlsxParser] 使用 xlrd 引擎失败: {e}")
        
        return data
    
    @staticmethod
    async def parse(file_path: str) -> Optional[str]:
        """
        解析 Excel/CSV 文件
        
        :param file_path: 文件路径
        :return: 文件内容
        """
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                data = await XlsxParser._read_data_from_excel(file_path)
                if not data:
                    logger.error(f"[XlsxParser] 无法解析 Excel 文件: {file_path}")
                    return None
            elif file_path.endswith('.csv'):
                try:
                    data = {'Sheet1': pd.read_csv(file_path, header=None)}
                except Exception as e:
                    logger.error(f"[XlsxParser] 解析 CSV 文件失败: {e}")
                    return None
            else:
                # 尝试作为 Excel 解析
                data = await XlsxParser._read_data_from_excel(file_path)
                if data is None:
                    try:
                        data = {'Sheet1': pd.read_csv(file_path, header=None)}
                    except Exception as e:
                        logger.error(f"[XlsxParser] 解析文件失败: {e}")
                        return None
                
                if data is None:
                    logger.error(f"[XlsxParser] 无法解析文件: {file_path}")
                    return None
            
            paragraphs = []
            for sheet_name, df in data.items():
                if len(data) > 1:
                    paragraphs.append(f"\n[工作表: {sheet_name}]")
                
                table_array = XlsxParser._extract_table_to_array(df)
                for row in table_array:
                    paragraphs.append(' | '.join(row))
            
            content = '\n'.join(paragraphs)
            return content if content.strip() else None
        except Exception as e:
            logger.exception(f"[XlsxParser] 解析 Excel/CSV 文件失败: {e}")
            return None

