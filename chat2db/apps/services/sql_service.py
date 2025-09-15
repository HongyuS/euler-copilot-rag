from typing import Any
import logging
import re
import json

from chat2db.apps.llm import LLM, GENERATE_SQL_PROMPT, REPAIR_SQL_PROMPT, RISK_EVALUATE_SQL
from chat2db.apps.services.database_service import DatabaseService
from chat2db.apps.schemas.enum_var import DatabaseType

from config.config import config


class SqlService:

    @staticmethod
    async def get_connection_and_table_info(
        database_type: DatabaseType,
        host: str,
        port: int,
        username: str,
        password: str,
        database: str,
        table_list: list[str] | None = None
    ) -> str:
        try:
            conn = await DatabaseService.connect_database(database_type, host, port, username, password, database)

            if table_list is None or len(table_list) == 0:
                table_list = await DatabaseService.list_tables(database_type, conn)
            table_ddls = {}
            for table in table_list:
                ddl = await DatabaseService.get_table_ddl(database_type, table, conn)
                table_ddls[table] = ddl

            table_info = "\n".join([f"表: {table}\nDDL:\n{ddl}" for table, ddl in table_ddls.items()])

            return conn, table_info
        except Exception as e:
            logging.error(f"\n[获取数据库连接和表信息失败]\n\n{e}")
            raise e

    @staticmethod
    async def generator(
        database_type: DatabaseType,
        goal: str,
        table_info: str,
        llm: LLM | None = None,
    ) -> str:
        """
        核心业务逻辑：生成 SQL
        - 传入 table_info 作为表信息。
        - 或提供数据库连接信息 host, port, username, password, database
        """
        logging.info(f"\n[生成目标]\n\n{goal}")

        if llm == None:
            llm = LLM(
                model_name=config["LLM_MODEL"],
                openai_api_base=config["LLM_URL"],
                openai_api_key=config["LLM_KEY"],
                max_tokens=config["LLM_MAX_TOKENS"],
                request_timeout=60,
                temperature=0.5,
            )

        prompt = GENERATE_SQL_PROMPT.format(
            database_type=database_type.value, table_info=table_info, question=goal
        )

        try:
            result = await llm.chat_with_model(prompt, "请给出你生成的 SQL 语句")
            sql = (await SqlService._extract_json(result))['command']
            logging.info(f"\n[生成SQL成功]\n\n{sql}")
            return sql

        except Exception as e:
            logging.error(f"\n[生成SQL失败]\n\n{e}")
            raise e

    @staticmethod
    async def repairer(
        database_type: DatabaseType,
        goal: str,
        table_info: str,
        error_sql: str,
        error_msg: str,
        llm: LLM | None = None,
    ) -> str:
        """
        核心业务逻辑：生成修复 SQL
        - 传入 table_info 作为表信息。
        - 或提供数据库连接信息 host, port, username, password, database
        """
        if llm == None:
            llm = LLM(
                model_name=config["LLM_MODEL"],
                openai_api_base=config["LLM_URL"],
                openai_api_key=config["LLM_KEY"],
                max_tokens=config["LLM_MAX_TOKENS"],
                request_timeout=60,
                temperature=0.5,
            )

        prompt = REPAIR_SQL_PROMPT.format(
            database_type=database_type.value,
            table_info=table_info,
            error_sql=error_sql,
            error_msg=error_msg,
            question=goal,
        )
        try:
            repair_sql = await llm.chat_with_model(prompt, "请给出你修复的 SQL 语句")
            logging.info(f"\n[修复SQL成功]\n\n{repair_sql}")
            return repair_sql
        
        except Exception as e:
            logging.error(f"\n[修复SQL失败]\n\n{e}")
            raise e

    @staticmethod
    async def executer(
        database_type: DatabaseType,
        sql: str,
        connection=None,
    ) -> list[dict]:
        """
        核心业务逻辑：执行 SQL
        """
        try:
            result = await DatabaseService.execute_sql(database_type, sql, connection)
            logging.info(f"\n[执行SQL]\n\n{sql}\n\n[执行结果]\n\n{result}")
            return result
        except Exception as e:
            logging.error(f"\n[执行失败]\n")
            raise e
        

    @staticmethod
    async def sql_handler(
        database_type: DatabaseType,
        goal: str,
        table_info: str,
        connection: Any,
        max_retries: int = 3,
    ) -> list[dict]:
        """
        核心业务逻辑：智能查询，支持语句异常自动修复
        """

        llm = LLM(
            model_name=config["LLM_MODEL"],
            openai_api_base=config["LLM_URL"],
            openai_api_key=config["LLM_KEY"],
            max_tokens=config["LLM_MAX_TOKENS"],
            request_timeout=60,
            temperature=0.5,
        )

        # 生成 SQL 查询语句
        sql = await SqlService.generator(database_type, goal, table_info, llm)

        risk = await SqlService.risk_analysis(database_type, goal, sql, table_info, llm=llm)

        ### 故意产生错误
        # sql = sql.replace("SELECT", "SELCT")
        ###

        # 初次尝试执行 SQL 查询
        retries = 0
        while retries <= max_retries:
            try:
                execute_result = await SqlService.executer(database_type, sql, connection=connection)
                return execute_result, sql, risk
            except Exception as e:
                if retries == max_retries:
                    logging.error(f"\n[重试次数已达到最大值]\n\nSQL 执行失败，最终错误：{e}")
                    raise e
                logging.error(f"\n[执行失败 - 尝试修复 {retries + 1}/{max_retries}]\n")
                repair_sql = await SqlService.repairer(
                    database_type=database_type,
                    goal=goal,
                    table_info=table_info,
                    error_sql=sql,
                    error_msg=str(e),
                    llm=llm,
                )

                sql = repair_sql
                retries += 1

        return []

    @staticmethod
    async def risk_analysis(
        database_type: DatabaseType,
        goal: str,
        sql: str,
        table_info: str,
        error_sql: str | None = None,
        error_msg: str | None = None,
        llm: LLM | None = None,
    ):
        
        if llm == None:
            llm = LLM(
                model_name=config["LLM_MODEL"],
                openai_api_base=config["LLM_URL"],
                openai_api_key=config["LLM_KEY"],
                max_tokens=config["LLM_MAX_TOKENS"],
                request_timeout=60,
                temperature=0.5,
            )

        prompt = RISK_EVALUATE_SQL.format(
            database_type=database_type.value,
            table_info=table_info,
            error_sql=error_sql,
            error_msg=error_msg,
            goal=goal,
            sql=sql,
        )

        try:
            result = await llm.chat_with_model(prompt, "请给出你评估的风险结果")
            risk = await SqlService._extract_json(result)
            logging.info(f"\n[风险分析成功]\n\n{risk}")
            return risk
        
        except Exception as e:
            logging.error(f"\n[风险分析失败]\n\n{type(e)}: {e}")
            raise e

    @staticmethod
    async def _extract_json(text: str):
        try: 
            match = re.search(r"\{.*?\}\s*$", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except json.JSONDecodeError as e:
            logging.error("\n[JSON解析失败]\n\n{e}")
            raise e

