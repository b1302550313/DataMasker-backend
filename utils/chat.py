import json

from langchain.llms.base import LLM
from typing import Optional, List, Dict, Any, Union
import requests

class CustomHTTPLLM(LLM):
    url: str  # 你的LLM推理接口的URL

    @property
    def _llm_type(self) -> str:
        return "custom_http_llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, message: Optional[List[Dict[str, str]]] = None) -> str:
        # 构造message列表
        message = message if message else []  # 如果有历史记录，直接使用
        message.append({"role": "user", "content": prompt})  # 添加用户输入

        # 构造请求数据
        data = {
                "messages": message
        }

        # 发送HTTP请求
        t = 0
        while t<5:
            try:
                response = requests.post(self.url, json=data)
                break
            except:
                t+=1

        # response.raise_for_status()  # 检查请求是否成功

        # 解析响应并返回生成的文本
        decoded_data = response.content.decode('utf-8')
        # 将字符串解析为 Python 字典
        json_data = json.loads(decoded_data)
        # 提取 content 的值
        content = json_data['res'][0]['content']
        # result = response.json()
        # 假设接口返回的数据格式是 {"data": {"response": "生成的文本"}}
        # return result.get("data", {}).get("response", "")
        return content
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"url": self.url}