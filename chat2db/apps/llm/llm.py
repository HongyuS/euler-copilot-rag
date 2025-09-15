# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import asyncio
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import re


class LLM:
    def __init__(self, model_name, openai_api_base, openai_api_key, request_timeout, max_tokens, temperature):
        self.client = ChatOpenAI(model_name=model_name,
                                 openai_api_base=openai_api_base,
                                 openai_api_key=openai_api_key,
                                 request_timeout=request_timeout,
                                 max_tokens=max_tokens,
                                 temperature=temperature)

    def assemble_chat(self, system_call, user_call):
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
            return
        await q.put(None)

    async def chat_with_model(self, chat, system_call, user_call, st_str: str = None, en_str: str = None):
        q = asyncio.Queue(maxsize=100)

        # 启动生产者任务
        producer_task = asyncio.create_task(self.data_producer(q, chat, system_call, user_call))
        content = ""
        while True:
            data = await q.get()
            if data is None:
                break
            content += data
        content = re.sub(r'.*?</think>\n?', '', content, flags=re.DOTALL)
        content = content.strip()
        return content
