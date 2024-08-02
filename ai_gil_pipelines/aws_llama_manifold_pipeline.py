import os
import boto3
from botocore.exceptions import ClientError
from schemas import OpenAIChatMessage
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import json

from utils.pipelines.main import pop_system_message


class Pipeline:
    class Valves(BaseModel):
        AWS_ACCESS_KEY_ID: str = ""
        AWS_SECRET_ACCESS_KEY: str = ""
        AWS_REGION: str = ""

    def __init__(self):
        self.type = "manifold"
        self.id = "aws_meta"
        self.name = "AWS Meta: "

        self.valves = self.Valves(
            **{
                "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", "your-access-key-id-here"),
                "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", "your-secret-access-key-here"),
                "AWS_REGION": os.getenv("AWS_REGION", "your-region-here"),
            }
        )
        self.client = self.create_bedrock_client()

    def create_bedrock_client(self):
        return boto3.client(
            service_name="bedrock-runtime",
            region_name=self.valves.AWS_REGION,
            aws_access_key_id=self.valves.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.valves.AWS_SECRET_ACCESS_KEY,
        )

    def get_meta_models(self):
        return [
            {"id": "meta.llama3-1-8b-instruct-v1:0", "name": "llama3.1_8B"},
            {"id": "meta.llama3-1-70b-instruct-v1:0", "name": "llama3.1_70B"},
            {"id": "meta.llama3-1-405b-instruct-v1:0", "name": "llama3.1_405B"},
        ]

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    async def on_valves_updated(self):
        self.client = self.create_bedrock_client()
        pass

    def pipelines(self) -> List[dict]:
        return self.get_meta_models()

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        try:
            # Remove unnecessary keys
            for key in ["user", "chat_id", "title"]:
                body.pop(key, None)

            processed_messages = ""

            for message in messages:
                content = message.get("content", "")
                role_tag = f"<|{message['role']}_id|>"
                processed_messages += f"{role_tag}\n\n{content}\n<|eot_id|>\n"

            system_message = (
                "You are an AI assistant. You will receive messages structured as follows: "
                "each message has a 'role' indicating if it's from 'user' or 'assistant', "
                "and 'content' containing the actual message. "
                "Please respond appropriately based on this structure."
                "When you respond, do not include the role tag, only the content. Since you will always be the assistant"
            )

            system_prompt = f" \n\n{system_message}\n<|eot_id|>\n" if system_message else ""

            # Combine the system prompt with the processed messages
            prompt = system_prompt + processed_messages

            # Prepare the payload
            payload = {
                "max_gen_len": body.get("max_tokens", 2048),
                "temperature": body.get("temperature", 0.8),
                "top_p": body.get("top_p", 0.9),
                "prompt": prompt,
            }
            return self.get_completion(model_id, payload)
        except Exception as e:
            return f"Error: {e}"

    def get_completion(self, model_id: str, payload: dict) -> str:
        print(f"Getting completion for model {model_id} with payload {payload}")
        response = self.client.invoke_model(modelId=model_id, body=json.dumps(payload))
        response_body = json.loads(response["body"].read())
        return response_body["generation"]
