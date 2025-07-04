import os
import uuid
from utils.my_tools.logger import logger as logging
from pandas import DataFrame
from docx.table import Table as DocxTable
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.parser.tools.split import split_tools


# TODO chunk和chunk_link可以封装成类


class BaseService:

    def __init__(self):
        self.vectorizer = None
        self.llm_max_tokens = None
        self.llm = None
        self.tokens = None

    async def init_service(self, llm_entity, llm_max_tokens, tokens, parser_method):
        self.parser_method = parser_method
        if llm_entity is None:
            self.llm = None
            self.llm_max_tokens = None
        else:
            self.llm = llm_entity
            self.llm_max_tokens = llm_max_tokens
        self.tokens = tokens
        self.vectorizer = TfidfVectorizer()

    @staticmethod
    def get_uuid():
        """
        获取uuid
        返回：
        生成的uuid
        """
        return uuid.uuid4()

    def check_similarity(self, text1, text2):
        """
        TODO :获取段落相似度，具体数值待微调
        """
        # 将文本转换为TF-IDF向量
        if len(text1) < len(text2)*10:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])

            # 计算余弦相似度
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            if cosine_sim > 0.85:
                return True
        return False

    def merge_texts(self, texts):
        now_len = 0
        now_text = ""
        new_texts = []
        for text in texts:
            if text['type'] == 'para':
                if text['text'] == "":
                    continue
                token_len = split_tools.get_tokens(text)
                if now_len + token_len < max(self.tokens // 2, 128) or (
                        now_len + token_len < self.tokens and self.check_similarity(now_text, text['text'])):
                    now_text += text['text'] + '\n'
                    now_len += token_len
                else:
                    new_texts.append({'text': now_text, 'type': 'para'})
                    now_text = text['text'] + '\n'
                    now_len = token_len
            else:
                if now_len:
                    new_texts.append({'text': now_text, 'type': 'para'})
                    now_text = ""
                    now_len = 0
                new_texts.append(text)
        if now_len:
            new_texts.append({'text': now_text, 'type': 'para'})
        return new_texts

    @staticmethod
    def split_sentences(text, TOKENS=1024):
        """
        分句，不超过Tokens数量
        """
        try:
            words = split_tools.split_words(text)
            current_length = 0
            current_sentence = ""
            result = []
            for word in words:
                current_sentence = current_sentence + word
                current_length = current_length + 1
                if current_length >= TOKENS:
                    result.append(current_sentence)
                    current_sentence = ""
                    current_length = 0
            result.append(current_sentence)
            return result
        except Exception as e:
            logging.error(f"split sentences error as {e}")
            return []

    def split_table(self, table):
        """
        按照行分表
        """

        if table is None:
            return []
        result = []
        new_table = []
        cell_num = 1
        try:
            if isinstance(table, DataFrame):
                for index, row in table.iterrows():
                    row_string_list = [s.replace('|', '||') for s in row.astype(str).tolist()]
                    cell_num = max(cell_num, len(row_string_list))
                    new_table.append(row_string_list)
            elif isinstance(table, DocxTable):
                if table.rows:
                    for row in table.rows:
                        row_string_list = [s.replace('|', '||') for s in (cell.text.strip() for cell in row.cells)]
                        cell_num = max(cell_num, len(row_string_list))
                        new_table.append(row_string_list)
            else:
                logging.error(f"table type Error as{type(table)}")
                return []
        except Exception as e:
            logging.error(f"split tables error as{e}")
            return []

        max_tokens = (self.tokens - cell_num) // cell_num
        for row in new_table:
            new_line = []
            max_len = 0
            for cell in row:
                cell = self.split_sentences(cell, max_tokens)
                if not cell:
                    cell = ['']
                new_line.append(cell)
                max_len = max(max_len, len(cell))
            for i in range(max_len):
                row_text = ' | '.join([cell[i] if len(cell) > i else ' ' for cell in new_line])
                row_text = row_text.replace('\n', '\\n')
                result.append(row_text)

        return result

    def package_to_chunk(self, **kwargs):
        """
        整合成chunk

        参数:
        - id (str, optional): 目标uuid，默认生成一个新的UUID
        - text (str, optional): 目标内容，默认为空字符串
        - tokens (int, optional): 词数，默认为0
        - status (str, optional): 状态，默认为空字符串
        - type_from (str, optional): 来源类型，默认为general
        - type_big (str, optional): 大类型，默认为para
        - type_small (str, optional): 小类型，默认为line
        - type_attr (str, optional): 属性类型，默认为normal
        - link_to (str, optional): 链接目标uuid，默认为空字符串
        - offset_in_document (int, optional): 在文档中的偏移量，默认为0

        返回:
        - dict: 包含chunk信息的字典
        """
        # TODO:可以进行封装
        default_values = {
            'id': self.get_uuid(),
            'text': "",
            'tokens': 0,
            'status': "",
            'type_from': 'general',
            'type_big': 'para',
            'type_small': 'line',
            'type_attr': 'normal',
            'link_to': "",
            'enabled': True,
            'local_offset': 0,
            'global_offset': 0,
        }

        # 更新默认值为传入的参数值
        for key, value in kwargs.items():
            if key in default_values:
                default_values[key] = value
        chunk_type = f"{default_values['type_from']}.{default_values['type_big']}." \
                     f"{default_values['type_small']}.{default_values['type_attr']}"

        # 构建chunk字典
        chunk = {
            'id': default_values['id'],
            'text': default_values['text'],
            'type': chunk_type,
            'tokens': default_values['tokens'],
            'global_offset': default_values['global_offset'],
            'local_offset': default_values['local_offset'],
            'enabled': default_values['enabled'],
            'status': default_values['status'],
            'link_to': default_values['link_to'],
        }

        return chunk

    def package_to_link(self, chunk_a, chunk_b, **kwargs):
        """
        打包link
        参数：
        - chunk_a (str): 出发chunk的id
        - chunk_b (str): 目标chunk的id
        - is_global (str, optional): link为全局边或者局部边，默认为local
        - structure (str, optional): link的小类，表示link属于line/tree/map，默认为line
        - model (str, optional): link的模型，默认为pre
        - jump (str or int, optional): 跳转值，默认为0

        返回：
        - dict: 包含link信息的字典
        """

        default_values = {
            'is_global': 'local',
            'structure': 'line',
            'model': 'pre',
            'jump': 0
        }

        # 更新默认值为传入的参数值
        for key, value in kwargs.items():
            if key in default_values:
                default_values[key] = value

        # 确保 jump 是字符串类型
        jump = str(default_values['jump'])

        # 构建 link 字典
        link_type = (f"{default_values['is_global']}.{default_values['model']}."
                     f"{default_values['structure']}.{jump}")
        link = {
            'id': self.get_uuid(),
            'chunk_a': chunk_a,
            'chunk_b': chunk_b,
            'type': link_type,
        }

        return link

    def build_chunks_by_lines(self, sentences):
        """
        chunks 连接函数
        sentences中需要type和text字段
        """
        sentences = self.merge_texts(sentences)
        chunks = []
        local_count = 0
        para_count = 0
        now_type = 'None'
        last_para = None
        last_local = None
        chunks_para = []
        local_offset = 0
        global_offset = 0
        for part in sentences:
            global_offset += 1
            local_offset += 1
            if now_type != part['type']:
                last_local = None
                local_offset = 0
            if part['type'] == now_type:
                local_count += 1
                type_attr = 'normal'
            else:
                type_attr = 'head'
                local_count = 0
            if part['type'] == 'para':
                link_to = last_para
                para_count += 1
            else:
                link_to = last_local

            now_type = part['type']
            if 'id' not in part:
                part['id'] = self.get_uuid()
            chunk = self.package_to_chunk(id=part["id"], text=part["text"], tokens=split_tools.get_tokens(part["text"]),
                                          link_to=link_to, status="", type_from="general", type_big=part["type"],
                                          type_small="line", type_attr=type_attr, global_offset=global_offset,
                                          local_offset=local_offset, )
            last_local = chunk['id']
            chunks.append(chunk)
            if now_type == 'para':
                last_para = chunk['id']
                chunks_para.append(chunk)
        return chunks

    def build_chunks_and_links_by_tree(self, tree: dict):
        """
        chunks 连接函数
        tree为dict表示的树结构，
        """
        chunks = []

        def get_edges(node, parent_id=None, dep=0):
            chunk = self.package_to_chunk(text=node["text"], tokens=split_tools.get_tokens(tree["text"]), status="",
                                          type_big=node["type"], type_small='tree', type_attr=node['type_attr'],
                                          global_offset=dep, link_to=parent_id, )
            node['id'] = chunk['id']
            chunks.append(chunk)

            # 如果当前节点有子节点，则遍历每个子节点
            if 'children' in node and node['children']:
                for child in node['children']:
                    # 递归处理子节点
                    get_edges(child, node['id'], dep + 1)

        get_edges(tree)

        chunk_links = []
        chunk_links.extend(self.edge_link(chunks, 'global', 'tree'))
        return chunks, chunk_links

    def build_chunk_links_by_line(self, chunks):
        """
        线性分割chunks并构建上下文关系
        """
        chunk_links = []
        chunks_para = []
        tmp_chunks = []
        for chunk in chunks:
            if chunk['type'] == 'para':
                if tmp_chunks is not None and len(tmp_chunks) > 0:
                    chunk_links.extend(self.edge_link(tmp_chunks, 'local', 'line'))
                tmp_chunks = []
            else:
                tmp_chunks.append(chunk)
        chunk_links.extend(self.edge_link(chunks_para, 'local', 'line'))
        chunk_links.extend(self.edge_link(chunks, 'global', 'line'))
        return chunk_links

    def edge_link(self, chunks, is_global, structure, **kwargs):
        """
        根据给定的块列表构建边缘链接。
        该函数通过遍历每个块，并为每个块与其链接的目标块创建双向链接数据。
        然后，根据这些链接数据生成链接对象列表。

        """
        links = []
        links_data = []
        for chunk in chunks:
            links_data.append({
                'chunk_a': chunk['id'],
                'chunk_b': chunk['link_to'],
                'is_global': is_global,
                'structure': structure,
                'model': 'next',
                'jump': 0
            })
            links_data.append({
                'chunk_a': chunk['link_to'],
                'chunk_b': chunk['id'],
                'is_global': is_global,
                'structure': structure,
                'model': 'pre',
                'jump': 0
            })

        for data in links_data:
            if data['chunk_a'] is None or data['chunk_b'] is None:
                continue
            links.append(
                self.package_to_link(chunk_a=data['chunk_a'], chunk_b=data['chunk_b'], is_global=data['is_global'],
                                     structure=data['structure'], model=data['model'], jump=data['jump'], ))
        return links

    async def insert_image_to_tmp_folder(self, image_bytes, image_id, image_extension):
        """
        插入图像字节流到临时文件夹中（用于插入到minIO）
        参数：
        - image_bytes: 图像字节流（可以是多个图像）
        - image_id: 用于保存图像文件的id
        """
        output_dir = None
        try:
            if not isinstance(type(image_bytes), list):
                image_bytes = [image_bytes]
            for image in image_bytes:
                output_dir = os.path.join('./parser', str(image_id))
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, str(image_id)+'.'+image_extension)
                with open(output_path, 'wb') as f:
                    f.write(image)
            return True
        except Exception as e:
            logging.error(f'Insert images {image_id} error: {e}')
            return False
