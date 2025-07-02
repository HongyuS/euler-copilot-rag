import asyncio
import os
import shutil
from uuid import uuid4
from data_chain.entities.enum import DocParseRelutTopology, ChunkParseTopology, ChunkType
from data_chain.parser.parse_result import ParseNode, ParseResult
from data_chain.parser.handler.base_parser import BaseParser
from data_chain.parser.tools.ocr_tool import OcrTool
from data_chain.logger.logger import logger as logging
from data_chain.parser.handler.md_zip_parser import MdZipParser
from data_chain.parser.tools.instruct_scan_tool import InstructScanTool


class FinePdfParser(BaseParser):
    name = 'pdf.fine'

    @staticmethod
    async def parser(file_path: str) -> ParseResult:
        if InstructScanTool.check_avx512_support():
            from marker.converters.pdf import PdfConverter
            from marker.models import create_model_dict
            from marker.config.parser import ConfigParser
            from marker.output import text_from_rendered, save_output
            fname_base = os.path.splitext(os.path.basename(file_path))[0]
            output_dir = os.path.dirname(file_path)
            md_path = os.path.join(output_dir, fname_base)
            config = {
                "output_format": "markdown",
                "ADDITIONAL_KEY": "VALUE"
            }
            config_parser = ConfigParser(config)

            converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=create_model_dict(),
                processor_list=config_parser.get_processors(),
                renderer=config_parser.get_renderer(),
                llm_service=config_parser.get_llm_service()
            )
            rendered = converter(file_path)
            if os.path.exists(md_path):
                shutil.rmtree(md_path)
            os.makedirs(md_path, exist_ok=True)
            save_output(rendered, md_path, fname_base)
            result = await MdZipParser.parser(md_path)
            return result
        else:
            logging.error("[FinePdfParser] 当前机器不支持 AVX-512，无法进行PDF解析")
            raise Exception("[FinePdfParser] 当前机器不支持 AVX-512，无法进行PDF解析")

