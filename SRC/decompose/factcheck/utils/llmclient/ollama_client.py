# Author: Lucia Makaiova
# Date: 14-04-2025
import json
import os
import ollama
from typing import List, Dict
from .base import BaseClient


class OllamaClient(BaseClient):
    """ Localhost LLM chatbot using the `ollama` Python library.
    See https://github.com/ollama/ollama for more info.
    """

    def __init__(
        self,
        model: str = "",
        api_config: dict = None,
        max_requests_per_minute=200,
        request_window=60,
    ):
        super().__init__(model, api_config, max_requests_per_minute, request_window)
        self.model = model
        if api_config and "LOCAL_API_URL" in api_config:
            os.environ["OLLAMA_HOST"] = api_config["LOCAL_API_URL"]

    def _call(self, messages: list[dict], **kwargs):
        response = ollama.chat(
            model=self.model,
            messages=messages,
        )
        return response['message']['content']

    def get_request_length(self, messages):
        return 1  

    def construct_message_list(
        self,
        prompt_list: List[str],
        system_role: str = "You are a helpful assistant designed to output JSON.",
    ):
        messages_list = []
        for prompt in prompt_list:
            messages = [
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt},
            ]
            messages_list.append(messages)
        return messages_list