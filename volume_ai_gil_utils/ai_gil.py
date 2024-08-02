import json
import boto3
import json
import os

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_default_region = os.getenv("AWS_REGION")


def get_model_id(model):
    if model == "llama3_8B":
        return "meta.llama3-1-8b-instruct-v1:0"
    elif model == "llama3_70B":
        return "meta.llama3-1-70b-instruct-v1:0"
    elif model == "llama3_405B":
        return "meta.llama3-1-405b-instruct-v1:0"
    elif model == "haiku":
        return "anthropic.claude-3-haiku-20240307-v1:0"
    elif model == "sonnet":
        return "anthropic.claude-3-5-sonnet-20240620-v1:0"
    else:
        raise ValueError("Invalid model ID")


def invoke_bedrock_with_single_text_message(
    prompt,
    system_prompt="",
    model="haiku",
    max_tokens=1024,
    verbose=False,
    temperature=0,
):
    """
    Since each call has a relation of 20x1 or more from input/output tokens
    PRICE-WISE Haiku is the best model for this task, as opposed to Llama3 8B
    which is cheaper when the relation is less than 13x1
    (given the prices of the models at the time of writing this code)
    """

    if model == "sonnet":
        aws_default_region = "us-east-1"  # Sonnet model is only available in us-east-1 as of 2024-07-31

    # Initialize the Amazon Bedrock runtime client
    client = boto3.client(
        "bedrock-runtime",
        region_name=aws_default_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    model_id = get_model_id(model)
    print(f"Model ID: {model_id}")
    print(f"region: {aws_default_region}")

    if "meta" in model_id:
        body = {
            "max_gen_len": max_tokens,
            "temperature": temperature,
            "prompt": f"[INST]{system_prompt}[/INST]\n{prompt}" if system_prompt else prompt,
        }
    elif "anthropic" in model_id:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                },
            ],
        }
    else:
        raise ValueError("Invalid model ID")

    print(f"Body: {body}")
    response = client.invoke_model(modelId=model_id, body=json.dumps(body))

    # Process and print the response
    result = json.loads(response.get("body").read())

    if verbose and "usage" in result.keys():
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])

        print("Invocation details:")
        print(f"- The input length is {input_tokens} tokens.")
        print(f"- The output length is {output_tokens} tokens.")

        print(f"- The model returned {len(output_list)} response(s):")
        for output in output_list:
            print(output["text"])
    elif verbose and "prompt_token_count" in result.keys():
        print(f"- The input length is {result['prompt_token_count']} tokens.")
        print(f"- The output length is {result['generation_token_count']} tokens.")
        print(f"- The model stopped because of {result['stop_reason']}.")
        print(f"The output is: \n\n{result['generation']}")

    return result
