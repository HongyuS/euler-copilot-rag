"""
深度 PDF 文件解析器（完整版）
基于 euler-copilot-rag 的 deep_pdf_parser.py 实现
支持：直接文本提取、OCR提取、表格检测和提取、图片提取、布局分析
"""
import os
import logging
import uuid
import re
from typing import Optional, List, Dict, Any, Tuple
import fitz  # PyMuPDF
from fitz import Page, Document
import cv2
import numpy as np
from sklearn.cluster import DBSCAN
import shutil

from parser.tools.ocr_tool import OcrTool

logger = logging.getLogger(__name__)


class Bbox:
    """边界框类"""
    def __init__(self, x0: float, y0: float, x1: float, y1: float):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

    def contains(self, other: 'Bbox') -> bool:
        """判断当前bbox是否包含另一个bbox"""
        return (self.x0 <= other.x0 and self.y0 <= other.y0 and
                self.x1 >= other.x1 and self.y1 >= other.y1)

    def overlaps(self, other: 'Bbox', threshold: float = 0.8) -> bool:
        """判断两个bbox是否重叠超过一定比例"""
        # 计算重叠区域
        x_overlap = max(0, min(self.x1, other.x1) - max(self.x0, other.x0))
        y_overlap = max(0, min(self.y1, other.y1) - max(self.y0, other.y0))
        overlap_area = x_overlap * y_overlap

        # 计算文本框的面积
        area = (self.x1 - self.x0) * (self.y1 - self.y0)
        if area == 0:
            return False

        # 如果重叠面积超过文本框面积的threshold，则认为重叠
        return (overlap_area / area) >= threshold


class ParseNodeWithBbox:
    """带边界框的解析节点"""
    def __init__(self, content: Any, node_type: str, bbox: Bbox, need_space: bool = False, need_newline: bool = False):
        self.content = content  # 内容（文本、表格行、图片二进制）
        self.type = node_type  # 'text', 'table', 'image'
        self.bbox = bbox
        self.is_need_space = need_space
        self.is_need_newline = need_newline


class DeepPdfParser:
    """深度 PDF 解析器，支持 OCR、表格、图片提取"""
    
    @staticmethod
    async def extract_text_from_page(
            page: Page, exclude_regions: List[Bbox] = None) -> List[ParseNodeWithBbox]:
        """直接从 PDF 页面提取文本"""
        nodes_with_bbox = []
        text_blocks = page.get_text("blocks")
        matrix = fitz.Matrix(2, 2)  # 设置缩放比例

        if exclude_regions is None:
            exclude_regions = []

        for block in text_blocks:
            if block[6] == 0:  # 确保是文本块
                text = block[4].strip()
                if not text:
                    continue
                bounding_box = block[:4]  # (x0, y0, x1, y1)
                block_bbox = Bbox(
                    x0=bounding_box[0]*matrix.a,
                    y0=bounding_box[1]*matrix.d,
                    x1=bounding_box[2]*matrix.a,
                    y1=bounding_box[3]*matrix.d
                )

                # 检查文本块是否在排除区域内
                should_exclude = False
                for region in exclude_regions:
                    if region.overlaps(block_bbox):
                        should_exclude = True
                        break

                if text and not should_exclude:
                    nodes_with_bbox.append(ParseNodeWithBbox(
                        content=text,
                        node_type='text',
                        bbox=block_bbox
                    ))
        return sorted(nodes_with_bbox, key=lambda x: (x.bbox.y0, x.bbox.x0))

    @staticmethod
    async def extract_text_from_page_by_ocr(
            image_path: str, exclude_regions: List[Bbox] = None) -> List[ParseNodeWithBbox]:
        """通过 OCR 从页面图片中提取文本"""
        text_nodes_with_bbox = []
        result = await OcrTool.ocr_from_image_path(image_path)
        if not result or not result[0]:
            return []
        
        for line in result[0]:
            try:
                # OCRv5 和 OCRv4 格式兼容
                if isinstance(line, (list, tuple)) and len(line) >= 2:
                    box = line[0]
                    text_info = line[1]
                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 1:
                        text = text_info[0].strip()
                    else:
                        text = str(text_info).strip()
                else:
                    continue
            except Exception as e:
                logger.warning(f"[DeepPdfParser] OCR结果解析失败: {e}")
                continue
            
            if not text:
                continue

            # 计算文本块边界框(左上x, 左上y, 右下x, 右下y)
            bbox_tuple = (min(p[0] for p in box), min(p[1] for p in box),
                         max(p[0] for p in box), max(p[1] for p in box))
            
            bbox = Bbox(
                x0=float(bbox_tuple[0]),
                y0=float(bbox_tuple[1]),
                x1=float(bbox_tuple[2]),
                y1=float(bbox_tuple[3])
            )

            text_nodes_with_bbox.append(ParseNodeWithBbox(
                content=text,
                node_type='text',
                bbox=bbox
            ))

        # 过滤排除区域
        new_text_nodes_with_bbox = []
        for text_node_with_bbox in text_nodes_with_bbox:
            overlaps = False
            for region in exclude_regions:
                if text_node_with_bbox.bbox.overlaps(region):
                    overlaps = True
                    break
            if not overlaps:
                new_text_nodes_with_bbox.append(text_node_with_bbox)
        
        new_text_nodes_with_bbox = sorted(new_text_nodes_with_bbox, key=lambda x: (x.bbox.y0, x.bbox.x0))
        return new_text_nodes_with_bbox

    @staticmethod
    async def detect_table(image_path: str) -> List[Bbox]:
        """检测图像中的表格区域"""
        image = cv2.imread(image_path)
        if image is None:
            return []
        
        # 提取绿色通道
        green = image[:, :, 1]
        channel = green

        # 二值化
        binary = cv2.adaptiveThreshold(channel, 255,
                                       cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY_INV, 15, 10)

        # 提取水平和垂直线
        horizontal = binary.copy()
        vertical = binary.copy()

        scale = 30
        h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal.shape[1] // scale, 1))
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical.shape[0] // scale))

        horizontal = cv2.erode(horizontal, h_kernel)
        horizontal = cv2.dilate(horizontal, h_kernel)
        vertical = cv2.erode(vertical, v_kernel)
        vertical = cv2.dilate(vertical, v_kernel)

        # 合并线条掩码
        mask = cv2.add(horizontal, vertical)

        # 轮廓检测
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        table_bboxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 基础过滤（小块排除）
            if w < 80 or h < 80:
                continue

            # 复杂度过滤
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) < 4 or len(approx) > 20:
                continue

            # 网格密度过滤
            region = mask[y:y+h, x:x+w]
            density = np.count_nonzero(region) / (w * h)
            if density < 0.02:
                continue

            table_bboxes.append(Bbox(
                x0=float(x), y0=float(y), x1=float(x + w), y1=float(y + h)
            ))

        # 按坐标排序
        table_bboxes = sorted(table_bboxes, key=lambda b: (b.y0, b.x0))

        # 合并相邻或重叠的表格区域
        merged_bboxes = []
        for bbox in table_bboxes:
            if not merged_bboxes:
                merged_bboxes.append(bbox)
                continue
            last = merged_bboxes[-1]
            overlap_x = min(last.x1, bbox.x1) - max(last.x0, bbox.x0)
            overlap_y = min(last.y1, bbox.y1) - max(last.y0, bbox.y0)

            if overlap_x > -20 and overlap_y > -20:
                merged = Bbox(
                    x0=min(last.x0, bbox.x0),
                    y0=min(last.y0, bbox.y0),
                    x1=max(last.x1, bbox.x1),
                    y1=max(last.y1, bbox.y1)
                )
                merged_bboxes[-1] = merged
            else:
                merged_bboxes.append(bbox)

        # 自适应扩展每个表格区域的边界框
        for bbox in merged_bboxes:
            width = bbox.x1 - bbox.x0
            height = bbox.y1 - bbox.y0
            # 计算长宽比例，按比例扩展
            if width > height:
                bbox.x0 = max(0, bbox.x0 - 30)
                bbox.y0 = max(0, bbox.y0 - 20)
                bbox.x1 += 30
                bbox.y1 += 20
            elif width < height:
                bbox.x0 = max(0, bbox.x0 - 20)
                bbox.y0 = max(0, bbox.y0 - 30)
                bbox.x1 += 20
                bbox.y1 += 30
            else:
                bbox.x0 = max(0, bbox.x0 - 20)
                bbox.y0 = max(0, bbox.y0 - 20)
                bbox.x1 += 20
                bbox.y1 += 20
        return merged_bboxes

    @staticmethod
    async def extract_table_from_page(
            image_path: str, merged_bboxes: List[Bbox]) -> Tuple[List[ParseNodeWithBbox], List[Bbox]]:
        """从页面图片中提取表格数据"""
        image = cv2.imread(image_path)
        if image is None:
            return [], []
        
        tmp_path = os.path.join(os.path.dirname(image_path), str(uuid.uuid4()))
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path)
        os.makedirs(tmp_path, exist_ok=True)
        
        nodes_with_bbox = []
        table_regions = []
        
        try:
            for bbox in merged_bboxes:
                try:
                    # 提取表格区域图像
                    table_image = image[int(bbox.y0): int(bbox.y1),
                                        int(bbox.x0): int(bbox.x1)]
                    table_image_path = os.path.join(tmp_path, f"table_{uuid.uuid4()}.png")
                    cv2.imwrite(table_image_path, table_image)
                    
                    result = await OcrTool.ocr_from_image_path(table_image_path)
                    if not result or not result[0]:
                        continue

                    cells = []
                    for line in result[0]:
                        try:
                            box = line[0]
                            text_info = line[1]
                            if isinstance(text_info, (list, tuple)) and len(text_info) >= 1:
                                text = text_info[0]
                            else:
                                text = str(text_info)

                            # 计算单元格边界框
                            cell_bbox = (min(p[0] for p in box), min(p[1] for p in box),
                                        max(p[0] for p in box), max(p[1] for p in box))

                            cells.append({
                                'x_center': (cell_bbox[0] + cell_bbox[2]) / 2,
                                'y_center': (cell_bbox[1] + cell_bbox[3]) / 2,
                                'text': text,
                                'box': box,
                                'bbox': cell_bbox
                            })
                        except Exception as e:
                            logger.warning(f"[DeepPdfParser] 解析单元格失败: {e}")
                            continue

                    if not cells or len(cells) < 4:
                        continue

                    # 使用DBSCAN聚类合并相近的单元格
                    coords = np.array([[cell['x_center'], cell['y_center']] for cell in cells])
                    clustering = DBSCAN(eps=20, min_samples=1).fit(coords)
                    labels = clustering.labels_

                    # 合并单元格
                    merged_cells = {}
                    for label, cell in zip(labels, cells):
                        if label not in merged_cells:
                            merged_cells[label] = []
                        merged_cells[label].append(cell)

                    # 计算合并后的单元格边界框
                    merged_cells_list = []
                    for label, group in merged_cells.items():
                        if not group:
                            continue
                        min_x = min(cell['bbox'][0] for cell in group)
                        min_y = min(cell['bbox'][1] for cell in group)
                        max_x = max(cell['bbox'][2] for cell in group)
                        max_y = max(cell['bbox'][3] for cell in group)
                        merged_cells_list.append({
                            'text': "\n".join(cell['text'] for cell in group),
                            'bbox': (min_x, min_y, max_x, max_y),
                            'box': [cell['box'] for cell in group]
                        })
                    
                    # 构建表格网格
                    all_x_coords = [cell['bbox'][0] for cell in cells] + [cell['bbox'][2] for cell in cells]
                    all_y_coords = [cell['bbox'][1] for cell in cells] + [cell['bbox'][3] for cell in cells]
                    all_x_coords = sorted(set(all_x_coords))
                    all_y_coords = sorted(set(all_y_coords))
                    
                    # 合并差异太小的x和y坐标
                    merged_x_coords = []
                    merged_y_coords = []
                    x_threshold = 5
                    y_threshold = 5
                    for x in all_x_coords:
                        if not merged_x_coords or x - merged_x_coords[-1] > x_threshold:
                            merged_x_coords.append(x)
                    for y in all_y_coords:
                        if not merged_y_coords or y - merged_y_coords[-1] > y_threshold:
                            merged_y_coords.append(y)
                    
                    if len(merged_x_coords) < 2 or len(merged_y_coords) < 2:
                        continue  # 不是标准网格结构

                    def get_id(num, coords):
                        """获取坐标在合并后的列表中的索引"""
                        if num < coords[0]:
                            return 0
                        if num >= coords[-1]:
                            return len(coords) - 1
                        l = 0
                        r = len(coords) - 1
                        while l + 1 < r:
                            mid = (l + r) // 2
                            if coords[mid] <= num:
                                l = mid
                            else:
                                r = mid
                        return l

                    # 创建表格
                    table = []
                    for row in range(len(merged_y_coords) - 1):
                        table.append([])
                        for col in range(len(merged_x_coords) - 1):
                            table[row].append("")
                    
                    sorted_cells = sorted(cells, key=lambda x: (
                        get_id(x['bbox'][1], merged_y_coords), get_id(x['bbox'][0], merged_x_coords)))
                    
                    for c in sorted_cells:
                        st_row_id = get_id(c['bbox'][1], merged_y_coords)
                        st_col_id = get_id(c['bbox'][0], merged_x_coords)
                        en_row_id = get_id(c['bbox'][3], merged_y_coords)
                        en_col_id = get_id(c['bbox'][2], merged_x_coords)
                        row_id = (st_row_id + en_row_id) // 2
                        col_id = (st_col_id + en_col_id) // 2
                        if row_id < len(table) and col_id < len(table[row_id]):
                            if len(table[row_id][col_id]) > 0:
                                table[row_id][col_id] += "\n"
                            table[row_id][col_id] += c['text']
                    
                    # 过滤空行
                    tmp_table = []
                    for i in range(len(table)):
                        is_empty = True
                        for j in range(len(table[i])):
                            if len(table[i][j]) > 0:
                                is_empty = False
                                break
                        if not is_empty:
                            tmp_table.append(table[i])
                    
                    # 过滤空列
                    if tmp_table:
                        drop_id_set = set()
                        for j in range(len(tmp_table[0])):
                            is_empty = True
                            for i in range(len(tmp_table)):
                                if len(re.sub(r'\s+', '', tmp_table[i][j])) > 0:
                                    is_empty = False
                                    break
                            if is_empty:
                                drop_id_set.add(j)
                        
                        final_table = []
                        for i in range(len(tmp_table)):
                            final_row = []
                            for j in range(len(tmp_table[i])):
                                if j not in drop_id_set:
                                    final_row.append(tmp_table[i][j])
                            final_table.append(final_row)
                        
                        if final_table:
                            # 为每行创建节点
                            for row in final_table:
                                nodes_with_bbox.append(ParseNodeWithBbox(
                                    content=row,
                                    node_type='table',
                                    bbox=bbox
                                ))
                            table_regions.append(bbox)
                except Exception as e:
                    logger.warning(f"[DeepPdfParser] 提取表格失败: {e}")
                    continue
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                try:
                    shutil.rmtree(tmp_path)
                except Exception:
                    pass

        return nodes_with_bbox, table_regions

    @staticmethod
    async def extract_image_from_page(
            pdf_doc: Document, page: Page) -> Tuple[List[ParseNodeWithBbox], List[Bbox]]:
        """从 PDF 页面提取图片"""
        nodes_with_bbox = []
        image_regions = []
        image_list = page.get_images(full=True)
        matrix = fitz.Matrix(2, 2)  # 设置缩放比例
        
        for image_info in image_list:
            try:
                # 获取图片的xref
                xref = image_info[0]
                # 提取基础图片（如果存在）
                base_image = pdf_doc.extract_image(xref)

                # 检查提取的图片是否有效
                if not base_image or "image" not in base_image:
                    logger.warning(f"[DeepPdfParser] 标准方法提取失败，尝试替代方法 xref={xref}")
                    continue

                # 检查位置信息
                rects = page.get_image_rects(xref)
                if not rects:
                    logger.warning(f"[DeepPdfParser] 找不到图片位置，尝试基于布局估算 xref={xref}")
                    width, height = base_image.get("width", 0), base_image.get("height", 0)
                    if width <= 0 or height <= 0:
                        logger.warning(f"[DeepPdfParser] 图片尺寸无效，跳过 xref={xref}")
                        continue
                    # 获取页面尺寸
                    page_width, page_height = page.rect.width * matrix.a, page.rect.height * matrix.d

                    # 基于图片大小的智能布局
                    if width > page_width * 0.8 and height > page_height * 0.8:
                        x0, y0 = 0, 0
                    elif width < page_width * 0.2 and height < page_height * 0.2:
                        x0 = page_width - width - 10
                        y0 = 10
                    else:
                        x0 = (page_width - width) / 2
                        y0 = (page_height - height) / 2

                    position = fitz.Rect(x0, y0, x0 + width, y0 + height)
                else:
                    position = rects[0]
                
                # 获取图片的二进制数据
                blob = base_image["image"]

                image_bbox = Bbox(
                    x0=position.x0 * matrix.a,
                    y0=position.y0 * matrix.d,
                    x1=position.x1 * matrix.a,
                    y1=position.y1 * matrix.d
                )

                nodes_with_bbox.append(ParseNodeWithBbox(
                    content=blob,
                    node_type='image',
                    bbox=image_bbox
                ))

                image_regions.append(image_bbox)
            except Exception as e:
                logger.exception(f"[DeepPdfParser] 提取图片失败: {e}")
                continue

        return nodes_with_bbox, image_regions

    @staticmethod
    async def merge_nodes_with_bbox(
            nodes_1: List[ParseNodeWithBbox],
            nodes_2: List[ParseNodeWithBbox]) -> List[ParseNodeWithBbox]:
        """合并两个节点列表，保持位置顺序"""
        if not nodes_1:
            return nodes_2
        if not nodes_2:
            return nodes_1

        max_x = 0
        index = 0
        nodes_3 = []

        for node in nodes_1:
            max_x = max(max_x, node.bbox.x1)
            if index < len(nodes_2):
                node_2 = nodes_2[index]
                while index < len(nodes_2) and node_2.bbox.x0 < max_x and node_2.bbox.y0 < node.bbox.y0:
                    nodes_3.append(node_2)
                    index += 1
                    if index < len(nodes_2):
                        node_2 = nodes_2[index]
            nodes_3.append(node)
        
        while index < len(nodes_2):
            node_2 = nodes_2[index]
            nodes_3.append(node_2)
            index += 1
        
        return nodes_3

    @staticmethod
    def image_related_node_in_link_nodes(nodes: List[ParseNodeWithBbox]) -> None:
        """建立图片与附近文本的关联关系（在此简化实现中暂不处理）"""
        # 在 mcp_center 的简化实现中，不需要建立链接关系
        pass

    @staticmethod
    def nodes_to_text(nodes: List[ParseNodeWithBbox]) -> str:
        """将节点列表转换为文本字符串"""
        content_parts = []
        
        for i, node in enumerate(nodes):
            # 添加换行（如果前一个节点需要换行）
            if i > 0 and nodes[i-1].is_need_newline:
                content_parts.append('')
            
            # 添加空格（如果前一个节点需要空格，且当前不需要换行）
            if i > 0 and nodes[i-1].is_need_space and not node.is_need_newline:
                # 在前一个内容和当前内容之间添加空格
                if content_parts and content_parts[-1]:
                    content_parts[-1] += ' '
            
            # 添加内容
            node_text = ''
            if node.type == 'text':
                node_text = node.content
            elif node.type == 'table':
                # 表格格式化为 Markdown 表格
                table_lines = ['[表格]:']
                if isinstance(node.content, list):
                    for row in node.content:
                        if isinstance(row, list):
                            table_lines.append(' | '.join(str(cell) for cell in row))
                        else:
                            table_lines.append(str(row))
                node_text = '\n'.join(table_lines)
            elif node.type == 'image':
                # 图片用占位符表示
                node_text = '[图片]'
            
            if node_text:
                content_parts.append(node_text)
        
        return '\n'.join(content_parts)

    @staticmethod
    async def parse(file_path: str) -> Optional[str]:
        """
        解析 PDF 文件，包括文本内容、表格和图片
        
        :param file_path: PDF 文件路径
        :return: 提取的文本内容，如果失败则返回 None
        """
        try:
            pdf_doc = fitz.open(file_path)
            if not pdf_doc:
                logger.error("[DeepPdfParser] 无法打开 PDF 文件")
                return None
            
            base_path = os.path.dirname(file_path)
            all_content = []
            
            for page_num in range(len(pdf_doc)):
                page = pdf_doc.load_page(page_num)
                
                # 渲染页面为图片
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image_path = os.path.join(base_path, f"deep_pdf_page_{page_num + 1}.png")
                pix.save(image_path)
                
                try:
                    # 先提取表格和图片，获取它们的区域
                    table_bboxes = await DeepPdfParser.detect_table(image_path)
                    table_nodes_with_bbox, table_regions = await DeepPdfParser.extract_table_from_page(
                        image_path, table_bboxes)
                    image_nodes_with_bbox, image_regions = await DeepPdfParser.extract_image_from_page(
                        pdf_doc, page)

                    # 合并排除区域
                    exclude_regions = table_regions + image_regions

                    # 提取文本时排除表格和图片区域
                    # 先尝试直接提取文本
                    text_nodes_with_bbox_1 = await DeepPdfParser.extract_text_from_page(page, exclude_regions)
                    text_nodes_with_bbox_2 = []
                    text_len_1 = 0
                    text_len_2 = 0
                    
                    for node in text_nodes_with_bbox_1:
                        if isinstance(node.content, str):
                            text_len_1 += len(node.content)
                    
                    # 如果直接提取的文本太少，使用 OCR
                    if text_len_1 < 100:
                        text_nodes_with_bbox_2 = await DeepPdfParser.extract_text_from_page_by_ocr(
                            image_path, exclude_regions)
                        for node in text_nodes_with_bbox_2:
                            if isinstance(node.content, str):
                                text_len_2 += len(node.content)
                    
                    # 选择效果更好的方法
                    if text_len_1 > text_len_2:
                        text_nodes_with_bbox = text_nodes_with_bbox_1
                    else:
                        text_nodes_with_bbox = text_nodes_with_bbox_2

                    # 合并所有节点
                    sub_nodes_with_bbox = await DeepPdfParser.merge_nodes_with_bbox(
                        text_nodes_with_bbox, table_nodes_with_bbox)
                    sub_nodes_with_bbox = await DeepPdfParser.merge_nodes_with_bbox(
                        sub_nodes_with_bbox, image_nodes_with_bbox)
                    sub_nodes_with_bbox = sorted(sub_nodes_with_bbox, key=lambda x: (x.bbox.y0, x.bbox.x0))
                    
                    # 标记最后一个节点需要空格
                    if sub_nodes_with_bbox:
                        sub_nodes_with_bbox[-1].is_need_space = True

                    # 根据 bbox 判断是否需要换行
                    for i in range(1, len(sub_nodes_with_bbox)):
                        vertical_distance = sub_nodes_with_bbox[i].bbox.y0 - sub_nodes_with_bbox[i-1].bbox.y1
                        height = sub_nodes_with_bbox[i].bbox.y1 - sub_nodes_with_bbox[i].bbox.y0
                        if vertical_distance > 0 and (vertical_distance > height * 0.3 or vertical_distance > 2):
                            sub_nodes_with_bbox[i-1].is_need_newline = True

                    # 根据 bbox 判断是否需要空格
                    for i in range(1, len(sub_nodes_with_bbox)):
                        horizontal_distance = sub_nodes_with_bbox[i].bbox.x0 - sub_nodes_with_bbox[i-1].bbox.x1
                        width = sub_nodes_with_bbox[i].bbox.x1 - sub_nodes_with_bbox[i].bbox.x0
                        if horizontal_distance > 0 and (horizontal_distance > width * 0.3 or horizontal_distance > 2):
                            sub_nodes_with_bbox[i-1].is_need_space = True

                    # 建立图片与文本的关联（简化实现中暂不处理）
                    DeepPdfParser.image_related_node_in_link_nodes(sub_nodes_with_bbox)

                    # 转换为文本
                    page_content = DeepPdfParser.nodes_to_text(sub_nodes_with_bbox)
                    if page_content.strip():
                        all_content.append(page_content)

                except Exception as e:
                    logger.warning(f"[DeepPdfParser] 第{page_num + 1}页处理失败: {e}")
                finally:
                    # 清理临时图片
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                        except Exception:
                            pass
            
            pdf_doc.close()

            if not all_content:
                logger.warning("[DeepPdfParser] PDF 文件中没有找到内容")
                return None

            return '\n\n'.join(all_content)

        except Exception as e:
            logger.exception(f"[DeepPdfParser] 解析 PDF 文件失败: {e}")
            return None
