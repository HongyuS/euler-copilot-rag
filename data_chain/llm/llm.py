# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import asyncio
from openai import AsyncOpenAI
from data_chain.logger.logger import logger


class LLM:
    def __init__(self, openai_api_key, openai_api_base, model_name, max_tokens, request_timeout=60, temperature=0.1):
        self.openai_api_key = openai_api_key
        self.openai_api_base = openai_api_base
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.request_timeout = request_timeout
        self.temperature = temperature
        self._client = AsyncOpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_api_base,
        )

    def assemble_chat(self, chat=None, system_call='', user_call=''):
        if chat is None:
            chat = []
        chat.append({"role": "system", "content": system_call})
        chat.append({"role": "user", "content": user_call})
        return chat

    async def create_stream(
            self, message):
        return await self._client.chat.completions.create(
            model=self.model_name,
            messages=message,  # type: ignore[]
            max_completion_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
            stream_options={"include_usage": True},
            timeout=300
        )  # type: ignore[]

    async def data_producer(self, q: asyncio.Queue, history, system_call, user_call):
        message = self.assemble_chat(history, system_call, user_call)
        stream = await self.create_stream(message)
        try:
            async for chunk in stream:
                if len(chunk.choices) == 0:
                    continue
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                else:
                    continue
                await q.put(content)
        except Exception as e:
            await q.put(None)
            err = f"[LLM] 流式输出生产者任务异常: {e}"
            logger.error(err)
            raise e
        await q.put(None)

    async def stream(self, chat, system_call, user_call):
        q = asyncio.Queue(maxsize=10)

        # 启动生产者任务
        asyncio.create_task(self.data_producer(q, chat, system_call, user_call))
        while True:
            data = await q.get()
            if data is None:
                break
            yield data

    async def nostream(self, chat, system_call, user_call, st_str: str = None, en_str: str = None):
        try:
            content = ''
            async for chunk in self.stream(chat, system_call, user_call):
                content += chunk
            content = content.strip()
            if st_str is not None:
                index = content.find(st_str)
                if index != -1:
                    content = content[index:]
            if en_str is not None:
                index = content[::-1].find(en_str[::-1])
                if index != -1:
                    content = content[:len(content)-index]
            logger.error(f"LLM nostream content: {content}")
        except Exception as e:
            err = f"[LLM] 非流式输出异常: {e}"
            logger.error("[LLM] %s", err)
            return ''
        return content
