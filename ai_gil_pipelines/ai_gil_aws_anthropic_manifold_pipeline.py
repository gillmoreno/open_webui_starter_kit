import os
import boto3
from botocore.exceptions import ClientError
from schemas import OpenAIChatMessage
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import json

from utils.pipelines.main import pop_system_message
from ai_gil_utils.private.prompts.video_script import TITLE_AND_HOOK_SYSTEM_PROMPT

AWS_REGION = "us-east-1"  # GIL: sonnet 3.5 is only located here


class Pipeline:
    class Valves(BaseModel):
        AWS_ACCESS_KEY_ID: str = ""
        AWS_SECRET_ACCESS_KEY: str = ""
        AWS_REGION: str = AWS_REGION

    def __init__(self):
        self.type = "manifold"
        self.id = "ai_gil_aws_anthropic"
        self.name = "AWS Anthropic: "

        self.valves = self.Valves(
            **{
                "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", "your-access-key-id-here"),
                "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", "your-secret-access-key-here"),
                "AWS_REGION": AWS_REGION,
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

    def get_anthropic_models(self):
        return [
            {
                "id": "anthropic.claude-3-haiku-20240307-v1:0",
                "name": "claude-3-haiku",
                "system_prompt": None,
            },
            {
                "id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
                "name": "claude-3.5-sonnet",
                "system_prompt": None,
            },
            {
                "id": "anthropic.claude-3-5-sonnet-20240620-v1:0__video_hook",
                "name": "claude-3.5-sonnet (video_hook)",
                "system_prompt": TITLE_AND_HOOK_SYSTEM_PROMPT,
            },
        ]

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        print("JOE ROGAN")
        print("JOE ROGAN")
        print("JOE ROGAN")
        print("JOE ROGAN")
        print("JOE ROGAN")
        print("JOE ROGAN")
        print("JOE ROGAN")
        print("JOE ROGAN")
        print("JOE ROGAN")
        print("JOE ROGAN")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    async def on_valves_updated(self):
        self.client = self.create_bedrock_client()
        pass

    def pipelines(self) -> List[dict]:
        return self.get_anthropic_models()

    def process_image(self, image_data):
        if image_data["url"].startswith("data:image"):
            mime_type, base64_data = image_data["url"].split(",", 1)
            media_type = mime_type.split(":")[1].split(";")[0]
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_data,
                },
            }
        else:
            return {
                "type": "image",
                "source": {"type": "url", "url": image_data["url"]},
            }

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        try:
            # Remove unnecessary keys
            for key in ["user", "chat_id", "title"]:
                body.pop(key, None)

            system_message, messages = pop_system_message(messages)

            system_prompt = next(
                (model["system_prompt"] for model in self.get_anthropic_models() if model["id"].startswith(model_id)),
                system_message,
            )

            model_id = model_id.split("__")[0]

            processed_messages = []
            image_count = 0
            total_image_size = 0

            for message in messages:
                processed_content = []
                if isinstance(message.get("content"), list):
                    for item in message["content"]:
                        if item["type"] == "text":
                            processed_content.append({"type": "text", "text": item["text"]})
                        elif item["type"] == "image_url":
                            if image_count >= 5:
                                raise ValueError("Maximum of 5 images per API call exceeded")

                            processed_image = self.process_image(item["image_url"])
                            processed_content.append(processed_image)

                            if processed_image["source"]["type"] == "base64":
                                image_size = len(processed_image["source"]["data"]) * 3 / 4
                            else:
                                image_size = 0

                            total_image_size += image_size
                            if total_image_size > 100 * 1024 * 1024:
                                raise ValueError("Total size of images exceeds 100 MB limit")

                            image_count += 1
                else:
                    processed_content = [{"type": "text", "text": message.get("content", "")}]

                processed_messages.append({"role": message["role"], "content": processed_content})

            # Prepare the payload
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": body.get("max_tokens", 4096),
                "temperature": body.get("temperature", 0.8),
                "top_k": body.get("top_k", 40),
                "top_p": body.get("top_p", 0.9),
                "stop_sequences": body.get("stop", []),
                "messages": processed_messages,
                **({"system": str(system_prompt)} if system_prompt else {}),
            }

            if body.get("stream", False):
                return self.stream_response(model_id, payload)
            else:
                return self.get_completion(model_id, payload)
        except ClientError as e:
            return f"Error: {e}"

    def stream_response(self, model_id: str, payload: dict) -> Generator:
        response = self.client.invoke_model_with_response_stream(
            modelId=model_id, contentType="application/json", accept="application/json", body=json.dumps(payload)
        )
        for event in response.get("body"):
            chunk = json.loads(event["chunk"]["bytes"].decode())
            if chunk["type"] == "content_block_start":
                yield chunk["content_block"]["text"]
            elif chunk["type"] == "content_block_delta":
                yield chunk["delta"]["text"]

    def get_completion(self, model_id: str, payload: dict) -> str:
        # print("JOE ROGAN: ", payload)
        response = self.client.invoke_model(modelId=model_id, body=json.dumps(payload))
        response_body = json.loads(response["body"].read())
        return response_body["content"][0]["text"]
