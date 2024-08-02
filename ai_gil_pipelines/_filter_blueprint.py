from typing import List, Optional
from pydantic import BaseModel
from schemas import OpenAIChatMessage
import os
import requests
import json

from utils.pipelines.main import (
    get_last_user_message,
    add_or_update_system_message,
    get_tools_specs,
)


class Pipeline:
    class Valves(BaseModel):
        pipelines: List[str] = []
        priority: int = 0

    def __init__(self):
        self.type = "filter"
        self.name = "Some crazy Filter"
        self.valves = self.Valves(
            **{
                "pipelines": ["*"],
            }
        )

    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        print(f"on_shutdown:{__name__}")
        pass

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Do something before the pipeline. So before the message goes through the LLM
        """
        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Do something after the pipeline. So after the message goes through the LLM
        """
        return body
