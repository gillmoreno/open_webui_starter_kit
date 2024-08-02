from typing import List, Union, Generator, Iterator
from schemas import OpenAIChatMessage
from pydantic import BaseModel

import os
import requests


class Pipeline:
    class Valves(BaseModel):
        PERPLEXITY_API_BASE_URL: str = "https://api.perplexity.ai"
        PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY")

    def __init__(self):
        self.type = "manifold"
        self.name = "Perplexity AI: "

        self.valves = self.Valves(**{"PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY")})

        self.pipelines = self.get_perplexity_models()

    async def on_startup(self):
        print(f"on_startup:{__name__}")

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")

    async def on_valves_updated(self):
        print(f"on_valves_updated:{__name__}")
        self.pipelines = self.get_perplexity_models()

    def get_perplexity_models(self):
        # For Perplexity AI, we'll hardcode the available models
        # You may want to update this list based on the latest available models
        return [
            {
                "id": "llama-3.1-sonar-small-128k-online",
                "name": "Llama 3.1 Sonar Small 128k Online",
            },
            # Add other available models here
        ]

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.valves.PERPLEXITY_API_KEY}",
        }

        payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise and concise",
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
        }

        try:
            r = requests.post(
                url=f"{self.valves.PERPLEXITY_API_BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
            )

            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

        except Exception as e:
            return f"Error: {e}"
