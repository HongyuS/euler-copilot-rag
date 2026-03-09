"""
Markdown 文件解析器
"""
import logging
import markdown
from bs4 import BeautifulSoup, Tag
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class MdParser:
    """Markdown 文档解析器"""
    
    @staticmethod
    def _extract_table_to_array(table_html: str) -> list:
        """提取表格为数组"""
        soup = BeautifulSoup(table_html, 'html.parser')
        rows = soup.find_all('tr')
        table_data = []
        for row in rows:
            cells = row.find_all(['th', 'td'])
            row_data = [cell.get_text(strip=True, separator=' ') for cell in cells]
            if row_data:
                table_data.append(row_data)
        return table_data
    
    @staticmethod
    def _get_image_blob(img_src: str) -> Optional[bytes]:
        """获取图片二进制数据"""
        if img_src.startswith(('http://', 'https://')):
            try:
                response = requests.get(img_src, timeout=3)
                response.raise_for_status()
                return response.content
            except requests.RequestException as e:
                logger.warning(f"[MdParser] 图片下载失败 {e}")
                return None
        return None
    
    @staticmethod
    def _build_subtree(html: str, current_level: int) -> list:
        """构建子树"""
        soup = BeautifulSoup(html, 'html.parser')
        root = soup.body if soup.body else soup
        current_level_elements = list(root.children)
        subtree = []
        valid_headers = ["h1", "h2", "h3", "h4", "h5", "h6"]
        
        while current_level_elements:
            element = current_level_elements.pop(0)
            if not isinstance(element, Tag):
                try:
                    text = element.get_text(strip=True)
                    if text:
                        subtree.append(text)
                except Exception:
                    pass
                continue
            
            if element.name == 'p' or element.name == 'ol' or element.name == 'hr' or element.name == 'ul' or element.name == 'div':
                inner_html = ''.join(str(child) for child in element.children)
                child_subtree = MdParser._build_subtree(inner_html, current_level + 1)
                if child_subtree:
                    subtree.extend(child_subtree)
                else:
                    text = element.get_text(strip=True)
                    if text:
                        subtree.append(text)
            elif element.name in valid_headers:
                try:
                    level = int(element.name[1:])
                except Exception:
                    level = current_level
                title = element.get_text().strip()
                
                content_elements = []
                while current_level_elements:
                    sibling = current_level_elements[0]
                    if sibling.name and sibling.name in valid_headers:
                        next_level = int(sibling.name[1:])
                    else:
                        next_level = level + 1
                    if next_level <= level:
                        break
                    content_elements.append(current_level_elements.pop(0))
                
                if title:
                    subtree.append(f"{'#' * level} {title}")
                
                if content_elements:
                    content_html = ''.join(str(el) for el in content_elements)
                    child_subtree = MdParser._build_subtree(content_html, level)
                    subtree.extend(child_subtree)
                else:
                    if title:
                        subtree.append(title)
            elif element.name == 'code':
                code_text = element.get_text().strip()
                if code_text:
                    subtree.append(f"```\n{code_text}\n```")
            elif element.name == 'li':
                para_text = element.get_text().strip()
                if para_text:
                    subtree.append(f"- {para_text}")
            elif element.name == 'img':
                img_src = element.get('src')
                if img_src:
                    subtree.append(f"[图片: {img_src}]")
            elif element.name == 'table':
                table_array = MdParser._extract_table_to_array(str(element))
                for row in table_array:
                    subtree.append(' | '.join(row))
        
        return subtree
    
    @staticmethod
    async def parse(file_path: str) -> Optional[str]:
        """
        解析 Markdown 文件
        
        :param file_path: 文件路径
        :return: 文件内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                markdown_text = f.read()
            
            # 将 Markdown 转换为 HTML
            html = markdown.markdown(markdown_text, extensions=['tables'])
            
            # 从 HTML 提取内容
            content_list = MdParser._build_subtree(html, 0)
            
            content = '\n'.join(content_list)
            return content if content.strip() else None
        except Exception as e:
            logger.exception(f"[MdParser] 解析 Markdown 文件失败: {e}")
            return None

