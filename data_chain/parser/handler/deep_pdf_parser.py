import asyncio
import os
import io
import fitz
from fitz import Page, Document
import numpy as np
from PIL import Image
from pandas import DataFrame
from paddleocr import PaddleOCR
from pydantic import BaseModel, Field
import uuid
import cv2
import re
from sklearn.cluster import DBSCAN
import shutil
from data_chain.entities.enum import DocParseRelutTopology, ChunkParseTopology, ChunkType
from data_chain.parser.parse_result import ParseNode, ParseResult
from data_chain.parser.handler.base_parser import BaseParser
from data_chain.logger.logger import logger as logging


class Bbox(BaseModel):
    x0: float = Field(..., description="左上角x坐标")
    x1: float = Field(..., description="右下角x坐标")
    y0: float = Field(..., description="左上角y坐标")
    y1: float = Field(..., description="右下角y坐标")

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

        # 如果重叠面积超过文本框面积的threshold，则认为重叠
        return (overlap_area / area) >= threshold


class ParseNodeWithBbox(BaseModel):
    node: ParseNode = Field(..., description="文本块的内容")
    bbox: Bbox = Field(..., description="文本块的边界框")


class DeepPdfParser(BaseParser):
    name = 'pdf.deep'
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # 使用中文语言模型

    @staticmethod
    async def extract_text_from_page(
            page: Page, exclude_regions: list[Bbox] = None) -> list[ParseNodeWithBbox]:
        nodes_with_bbox = []
        text_blocks = page.get_text("blocks")
        matrix = fitz.Matrix(2, 2)  # 设置缩放比例

        # 如果没有提供排除区域，创建一个空列表
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
                        node=ParseNode(
                            id=uuid.uuid4(),
                            lv=0,
                            parse_topology_type=ChunkParseTopology.GRAPHNODE,
                            content=text,
                            type=ChunkType.TEXT,
                            link_nodes=[],
                        ),
                        bbox=block_bbox
                    ))
        return sorted(nodes_with_bbox, key=lambda x: (x.bbox.y0, x.bbox.x0))

    @staticmethod
    async def extract_text_from_page_by_ocr(
            image_path: str, exclude_regions: list[Bbox] = None) -> list[ParseNodeWithBbox]:
        text_nodes_with_bbox = []
        image = cv2.imread(image_path)
        result = DeepPdfParser.ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return []
        for line in result[0]:
            try:
                box = line[0]
                text = line[1][0].strip()
            except Exception as e:
                err = f"[DeepPdfParser] OCR识别失败: {e}"
                logging.error("[DeepPdfParser] %s", err)
                continue
            if not text:
                continue

            # 计算文本块边界框(左上x, 左上y, 右下x, 右下y)
            bbox = (min(p[0] for p in box), min(p[1] for p in box),
                    max(p[0] for p in box), max(p[1] for p in box))

            text_nodes_with_bbox.append(ParseNodeWithBbox(
                node=ParseNode(
                    id=uuid.uuid4(),
                    lv=0,
                    parse_topology_type=ChunkParseTopology.GRAPHNODE,
                    content=text,
                    type=ChunkType.TEXT,
                    link_nodes=[],
                ),
                bbox=Bbox(
                    x0=float(bbox[0]),
                    y0=float(bbox[1]),
                    x1=float(bbox[2]),
                    y1=float(bbox[3])
                )
            ))

        new_text_nodes_with_bbox = []
        for text_node_with_bbox in text_nodes_with_bbox:
            # 检查文本块是否与排除区域重叠
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
    async def detect_table(image_path: str) -> list[Bbox]:
        """
        检测图像中的表格，返回表格区域及其内容
        """

        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 使用改进的表格检测算法
        # 二值化
        binary = cv2.adaptiveThreshold(
            ~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -10
        )

        # 水平和垂直线检测
        horizontal = binary.copy()
        vertical = binary.copy()

        # 定义水平线和垂直线的结构元素
        cols = horizontal.shape[1]
        horizontal_size = cols // 30
        horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
        horizontal = cv2.erode(horizontal, horizontalStructure)
        horizontal = cv2.dilate(horizontal, horizontalStructure)

        rows = vertical.shape[0]
        vertical_size = rows // 30
        verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))
        vertical = cv2.erode(vertical, verticalStructure)
        vertical = cv2.dilate(vertical, verticalStructure)

        # 合并水平和垂直线
        mask = horizontal + vertical

        # 检测轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        table_bboxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # 基本过滤：过滤小区域
            if w < 100 or h < 100:
                continue

            # 计算轮廓面积与边界框面积的比率
            area = cv2.contourArea(contour)
            rect_area = w * h
            area_ratio = area / rect_area

            # 计算宽高比
            aspect_ratio = w / h if h != 0 else float('inf')

            # 表格通常具有较高的面积比率和适当的宽高比
            if area_ratio < 0.5 or (aspect_ratio < 0.3 or aspect_ratio > 5):
                continue

            # 提取候选区域
            region = mask[y:y+h, x:x+w]

            # 计算网格密度 - 表格应该有明显的网格结构
            grid_density = np.count_nonzero(region) / (w * h)

            # 表格通常具有较高的网格密度
            if grid_density < 0.05:
                continue

            # 计算轮廓的复杂度
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            complexity = len(approx)

            # 表格轮廓通常较简单，而非表格图形可能更复杂
            if complexity > 20:
                continue

            table_bboxes.append(Bbox(
                x0=float(x),
                y0=float(y),
                x1=float(x + w),
                y1=float(y + h)
            ))
        # 合并相近的表格区域
        table_bboxes = sorted(table_bboxes, key=lambda bbox: (bbox.y0, bbox.x0))
        merged_bboxes = []
        for bbox in table_bboxes:
            if not merged_bboxes:
                merged_bboxes.append(bbox)
                continue
            last_bbox = merged_bboxes[-1]
            # 检查当前bbox是否与上一个bbox相邻或重叠
            if (abs(bbox.x0 - last_bbox.x1) < 10 and abs(bbox.y0 - last_bbox.y0) < 10) or \
               (abs(bbox.y0 - last_bbox.y1) < 10 and abs(bbox.x0 - last_bbox.x0) < 10):
                # 合并两个bbox
                merged_bboxes[-1] = Bbox(
                    x0=min(last_bbox.x0, bbox.x0),
                    y0=min(last_bbox.y0, bbox.y0),
                    x1=max(last_bbox.x1, bbox.x1),
                    y1=max(last_bbox.y1, bbox.y1)
                )
            else:
                merged_bboxes.append(bbox)
        return merged_bboxes

    @staticmethod
    async def extract_table_from_page(image_path: str, merged_bboxes: list[Bbox]) -> tuple[list[ParseNodeWithBbox], list[Bbox]]:
        """
        对表格图像进行OCR识别并提取表格数据，支持合并单元格处理
        """
        image = cv2.imread(image_path)
        tmp_path = os.path.join(os.path.dirname(image_path), str(uuid.uuid4()))
        if os.path.exists(tmp_path):
            shutil.rmtree(tmp_path)
        os.makedirs(tmp_path)
        nodes_with_bbox = []
        table_regions = []
        for index in range(len(merged_bboxes)):
            try:
                # 提取表格区域图像
                table_image = image[int(merged_bboxes[index].y0): int(merged_bboxes[index].y1),
                                    int(merged_bboxes[index].x0): int(merged_bboxes[index].x1)]
                table_image_path = os.path.join(tmp_path, f"table_{uuid.uuid4()}.png")
                cv2.imwrite(table_image_path, table_image)
                result = DeepPdfParser.ocr.ocr(table_image_path, cls=True)

                if not result or not result[0]:
                    return []

                cells = []
                for line in result[0]:
                    box = line[0]
                    text = line[1][0]

                    # 计算单元格边界框(左上x, 左上y, 右下x, 右下y)
                    bbox = (min(p[0] for p in box), min(p[1] for p in box),
                            max(p[0] for p in box), max(p[1] for p in box))

                    cells.append({
                        'x_center': (bbox[0] + bbox[2]) / 2,
                        'y_center': (bbox[1] + bbox[3]) / 2,
                        'text': text,
                        'box': box,
                        'bbox': bbox
                    })

                if not cells:
                    return []
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
                cell = merged_cells_list
                all_x_coords = [cell['bbox'][0] for cell in cells] + [cell['bbox'][2] for cell in cells]
                all_y_coords = [cell['bbox'][1] for cell in cells] + [cell['bbox'][3] for cell in cells]
                all_x_coords = sorted(set(all_x_coords))
                all_y_coords = sorted(set(all_y_coords))
                # 合并差异太小的x和y坐标
                merged_x_coords = []
                merged_y_coords = []
                x_threshold = 5  # x坐标合并阈值
                y_threshold = 5  # y坐标合并阈值
                for x in all_x_coords:
                    if not merged_x_coords or x - merged_x_coords[-1] > x_threshold:
                        merged_x_coords.append(x)
                for y in all_y_coords:
                    if not merged_y_coords or y - merged_y_coords[-1] > y_threshold:
                        merged_y_coords.append(y)

                def get_id(num, coords):
                    """获取坐标在合并后的列表中的索引"""
                    if num < coords[0]:
                        return 0
                    if num >= coords[-1]:
                        return len(coords) - 1
                    l = 0
                    r = len(coords)-1
                    while l+1 < r:
                        mid = (l + r) // 2
                        if coords[mid] <= num:
                            l = mid
                        else:
                            r = mid
                    return l
                table = []
                for row in range(len(merged_y_coords) - 1):
                    table.append([])
                    for col in range(len(merged_x_coords) - 1):
                        table[row].append("")
                cell = sorted(cells, key=lambda x: (
                    get_id(x['bbox'][1], merged_y_coords), get_id(x['bbox'][0], merged_x_coords)))
                for c in cell:
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
                tmp_table = []
                for i in range(len(table)):
                    is_empty = True
                    for j in range(len(table[i])):
                        if len(table[i][j]) > 0:
                            is_empty = False
                            break
                    if not is_empty:
                        tmp_table.append(table[i])
                drop_id_set = set()
                for j in range(0, len(tmp_table[0])):
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
                if not final_table:
                    continue
                for row in final_table:
                    node = ParseNode(
                        id=uuid.uuid4(),
                        lv=0,
                        parse_topology_type=ChunkParseTopology.GRAPHNODE,
                        content=row,
                        type=ChunkType.TABLE,
                        link_nodes=[],
                    )
                    nodes_with_bbox.append(ParseNodeWithBbox(
                        node=node,
                        bbox=Bbox(
                            x0=merged_bboxes[index].x0,
                            y0=merged_bboxes[index].y0,
                            x1=merged_bboxes[index].x1,
                            y1=merged_bboxes[index].y1
                        )
                    ))
                table_regions.append(Bbox(
                    x0=merged_bboxes[index].x0,
                    y0=merged_bboxes[index].y0,
                    x1=merged_bboxes[index].x1,
                    y1=merged_bboxes[index].y1
                ))
            except Exception as e:
                err = f"[DeepPdfParser] 提取表格失败: {e}"
                logging.error("[DeepPdfParser] %s", err)
                continue
        return nodes_with_bbox, table_regions

    @staticmethod
    async def extract_image_from_page(pdf_doc: Document, page: Page) -> tuple[list[ParseNodeWithBbox], list[Bbox]]:
        nodes_with_bbox = []
        image_regions = []  # 存储图片区域的bbox
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
                    logging.warning("[DeepPdfParser] 标准方法提取失败，尝试替代方法 xref=%s", xref)
                    continue

                # 检查位置信息
                rects = page.get_image_rects(xref)
                if not rects:
                    logging.warning("[DeepPdfParser] 找不到图片位置，尝试基于布局估算 xref=%s", xref)
                    width, height = base_image.get("width", 0), base_image.get("height", 0)
                    if width <= 0 or height <= 0:
                        logging.warning("[DeepPdfParser] 图片尺寸无效，跳过 xref=%s", xref)
                        continue
                    # 获取页面尺寸
                    page_width, page_height = page.rect.width * matrix.a, page.rect.height * matrix.d

                    # 方法1: 默认居中布局
                    x0 = (page_width - width) / 2
                    y0 = (page_height - height) / 2

                    # 方法2: 考虑文本布局，假设图片在页面上半部分
                    # 这里可以集成文本布局分析，例如获取页面上的文本块位置
                    # 然后避免与文本重叠

                    # 方法3: 基于图片大小的智能布局
                    # 如果图片很大，可能是全页图片，位置应从(0,0)开始
                    if width > page_width * 0.8 and height > page_height * 0.8:
                        x0, y0 = 0, 0
                    # 如果图片很小，可能是图标或装饰，可能在角落
                    elif width < page_width * 0.2 and height < page_height * 0.2:
                        # 放在右上角作为默认位置
                        x0 = page_width - width - 10  # 留出边距
                        y0 = 10  # 留出边距

                    position = fitz.Rect(x0, y0, x0 + width, y0 + height)
                else:
                    position = rects[0]
                # 获取图片的二进制数据
                blob = base_image["image"]

                image_bbox = Bbox(
                    x0=position.x0*matrix.a,
                    y0=position.y0*matrix.d,
                    x1=position.x1*matrix.a,
                    y1=position.y1*matrix.d
                )

                nodes_with_bbox.append(ParseNodeWithBbox(
                    node=ParseNode(
                        id=uuid.uuid4(),
                        lv=0,
                        parse_topology_type=ChunkParseTopology.GRAPHNODE,
                        content=blob,
                        type=ChunkType.IMAGE,
                        link_nodes=[],
                    ),
                    bbox=image_bbox
                ))

                image_regions.append(image_bbox)
            except Exception as e:
                err = "提取图片失败"
                logging.exception("[DeepPdfParser] %s", err)
                continue

        return nodes_with_bbox, image_regions

    @staticmethod
    async def image_related_text(
            image_node_with_bbox: ParseNodeWithBbox, text_nodes_with_bbox: list[ParseNodeWithBbox]):
        image_x0, image_y0, image_x1, image_y1 = image_node_with_bbox.bbox.x0, image_node_with_bbox.bbox.y0, \
            image_node_with_bbox.bbox.x1, image_node_with_bbox.bbox.y1
        threshold = 100
        image_x0 -= threshold
        image_y0 -= threshold
        image_x1 += threshold
        image_y1 += threshold
        for text_node_with_bbox in text_nodes_with_bbox:
            text_x0, text_y0, text_x1, text_y1 = text_node_with_bbox.bbox.x0, text_node_with_bbox.bbox.y0, \
                text_node_with_bbox.bbox.x1, text_node_with_bbox.bbox.y1
            # 检查文本是否水平相邻
            horizontally_adjacent = (text_x1 >= image_x0 - threshold and text_x0 <= image_x1 + threshold)
            # 检查文本是否垂直相邻
            vertically_adjacent = (text_y1 >= image_y0 - threshold and text_y0 <= image_y1 + threshold)
            # 检查文本是否相交或相邻
            if horizontally_adjacent and vertically_adjacent:
                image_node_with_bbox.node.link_nodes.append(text_node_with_bbox.node)

    @staticmethod
    async def merge_nodes_with_bbox(
            nodes_1: list[ParseNodeWithBbox],
            nodes_2: list[ParseNodeWithBbox]) -> list[ParseNodeWithBbox]:
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
    async def parser(file_path: str) -> ParseResult:
        try:
            pdf_doc = fitz.open(file_path)
        except Exception as e:
            err = "无法打开pdf文件"
            logging.exception("[DeepPdfParser] %s", err)
            raise e
        base_path = os.path.dirname(file_path)
        nodes_with_bbox = []
        page_number = 0
        for page_num in range(len(pdf_doc)):
            page = pdf_doc.load_page(page_num)
            image = page.get_pixmap(
                matrix=fitz.Matrix(2, 2), alpha=False
            )  # 可以调整缩放比例
            image_path = os.path.join(base_path, f"page_{page_number + 1}.png")
            image.save(image_path)
            # 先提取表格和图片，获取它们的区域
            table_bboxes = await DeepPdfParser.detect_table(image_path)
            table_nodes_with_bbox, table_regions = await DeepPdfParser.extract_table_from_page(image_path, table_bboxes)
            image_nodes_with_bbox, image_regions = await DeepPdfParser.extract_image_from_page(pdf_doc, page)

            # 合并排除区域
            exclude_regions = table_regions + image_regions

            # 提取文本时排除表格和图片区域
            text_nodes_with_bbox = await DeepPdfParser.extract_text_from_page(page, exclude_regions)
            if not text_nodes_with_bbox:
                text_nodes_with_bbox = await DeepPdfParser.extract_text_from_page_by_ocr(
                    image_path, exclude_regions)
            # 合并所有节点
            sub_nodes_with_bbox = await DeepPdfParser.merge_nodes_with_bbox(
                text_nodes_with_bbox, table_nodes_with_bbox)
            sub_nodes_with_bbox = await DeepPdfParser.merge_nodes_with_bbox(
                sub_nodes_with_bbox, image_nodes_with_bbox)

            nodes_with_bbox.extend(sub_nodes_with_bbox)
            page_number += 1
        for i in range(1, len(nodes_with_bbox)):
            '''根据bbox判断是否要进行换行'''
            if nodes_with_bbox[i].bbox.y0 > nodes_with_bbox[i-1].bbox.y1 + 1:
                nodes_with_bbox[i].node.is_need_newline = True

        nodes = [node_with_bbox.node for node_with_bbox in nodes_with_bbox]
        DeepPdfParser.image_related_node_in_link_nodes(nodes)  # 假设这个方法在别处定义
        parse_result = ParseResult(
            parse_topology_type=DocParseRelutTopology.GRAPH,
            nodes=nodes
        )
        for node in parse_result.nodes:
            if node.type == ChunkType.IMAGE:
                # 处理图片节点
                continue
        return parse_result
