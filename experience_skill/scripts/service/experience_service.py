import jieba
import os
import markdown
from bs4 import BeautifulSoup
import yaml
from ENUM.exprience import ExperienceType, ExperienceStatus
from schema.exprience import Experience


class ExperienceService:
    @staticmethod
    def filter_special_characters(text: str) -> str:

        def escape_fts_word(word: str) -> str:
            # 包含以下任意字符时，整体作为短语用双引号包裹，避免触发 FTS5 语法解析
            special_chars = [
                '"',
                "'",
                "(",
                ")",
                "*",
                ":",
                "?",
                "+",
                "-",
                "|",
                "&",
                "{",
                "}",
                "[",
                "]",
                "^",
                "$",
                "\\",
                "/",
                "!",
                "~",
                ";",
                ",",
                ".",
                " ",
                "%",
            ]
            if any(char in word for char in special_chars):
                escaped_word = word.replace('"', '""')
                return f'"{escaped_word}"'
            return word

        try:
            words = jieba.cut(text)
            words = [word.strip() for word in words if word.strip()]
            if not words:
                return escape_fts_word(text)
            escaped_words = [escape_fts_word(word) for word in words]
            return " ".join(escaped_words)
        except Exception:
            return ""

    @staticmethod
    def md_to_structured_json(md_content: str) -> dict:
        """
        第一步：把 Markdown 转成 标准 JSON 结构化数据
        """
        # 1. MD 转 HTML
        html = markdown.markdown(md_content, extensions=["tables"])

        # 2. 结构化解析 HTML（最稳健的方式）
        soup = BeautifulSoup(html, "html.parser")
        text_content = soup.get_text(separator=" ", strip=True)

        # 3. 解析成键值对结构（name / description / keywords）→ 结构化 JSON
        result = {}

        # 纯字符串切割，无正则，干净稳定
        if "name:" in text_content:
            _, after_name = text_content.split("name:", 1)
            if "description:" in after_name:
                result["name"], rest = after_name.split("description:", 1)
                result["name"] = result["name"].strip()

                if "keywords:" in rest:
                    desc, kw_part = rest.split("keywords:", 1)
                    result["description"] = desc.strip()

                    # 彻底清理 keywords 中的 [] 符号
                    kw_str = kw_part.strip().strip("[]")
                    result["keywords"] = [
                        k.strip() for k in kw_str.split(",") if k.strip()
                    ]

        return result

    @staticmethod
    async def add_experiences(
        experience_type: ExperienceType, source: str
    ) -> Experience:
        """
        添加Experience
        """
        description = ""
        keywords = []
        if experience_type == ExperienceType.SKILL:
            path = os.path.join(source, "SKILL.md")
            if not os.path.exists(path):
                raise FileNotFoundError(f"SKILL.md not found in {source}")
            md_content = markdown.markdown(open(path, "r", encoding="utf-8").read())
            structured_data = ExperienceService.md_to_structured_json(md_content)
        elif experience_type == ExperienceType.WIKI:
            path = os.path.join(source, "WIKI.md")
            if not os.path.exists(path):
                raise FileNotFoundError(f"WIKI.md not found in {source}")
            structured_data = yaml.safe_load(open(path, "r", encoding="utf-8"))
        description = structured_data.get("description", "")
        keywords = structured_data.get("keywords", [])
        description = ExperienceService.filter_special_characters(description)
        keywords = " ".join(
            [
                ExperienceService.filter_special_characters(keyword)
                for keyword in keywords
            ]
        )
