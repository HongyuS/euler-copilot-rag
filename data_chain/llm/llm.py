# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import asyncio
import time
import re
import json
import tiktoken
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from data_chain.logger.logger import logger as logging


class LLM:
    def __init__(self, openai_api_key, openai_api_base, model_name, max_tokens, request_timeout=60, temperature=0.1):
        self.openai_api_key = openai_api_key
        self.openai_api_base = openai_api_base
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.request_timeout = request_timeout
        self.temperature = temperature
        self.client = ChatOpenAI(model_name=model_name,
                                 openai_api_base=openai_api_base,
                                 openai_api_key=openai_api_key,
                                 request_timeout=request_timeout,
                                 max_tokens=max_tokens,
                                 temperature=temperature)

    def assemble_chat(self, chat=None, system_call='', user_call=''):
        if chat is None:
            chat = []
        chat.append(SystemMessage(content=system_call))
        chat.append(HumanMessage(content=user_call))
        return chat

    async def data_producer(self, q: asyncio.Queue, history, system_call, user_call):
        message = self.assemble_chat(history, system_call, user_call)
        try:
            async for frame in self.client.astream(message):
                await q.put(frame.content)
        except Exception as e:
            await q.put(None)
            err = f"[LLM] 流式输出生产者任务异常: {e}"
            logging.error("[LLM] %s", err)
            raise e
        await q.put(None)

    async def stream(self, chat, system_call, user_call):
        q = asyncio.Queue(maxsize=10)

        # 启动生产者任务
        producer_task = asyncio.create_task(self.data_producer(q, chat, system_call, user_call))
        while True:
            data = await q.get()
            if data is None:
                break
            yield data

    async def nostream(self, chat, system_call, user_call, st_str: str = None, en_str: str = None):
        try:
            content = ''
            async for chunk in self.client.astream(self.assemble_chat(chat, system_call, user_call)):
                content += chunk.content
            content = re.sub(r'.*?</think>\n?', '', content, flags=re.DOTALL)
            content = content.strip()
            if st_str is not None:
                index = content.find(st_str)
                if index != -1:
                    content = content[index:]
            if en_str is not None:
                index = content[::-1].find(en_str[::-1])
                if index != -1:
                    content = content[:len(content)-index]
            logging.error("[LLM] 非流式输出内容: %s", content)
        except Exception as e:
            err = f"[LLM] 非流式输出异常: {e}"
            logging.error("[LLM] %s", err)
            return ''
        return content
