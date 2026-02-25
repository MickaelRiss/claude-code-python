import argparse
import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "Read",
                "description": "Read and return the contents of the file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read",
                        }
                    },
                    "required": ["file_path"],
                },
            },
        }
    ]

    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=[{"role": "user", "content": args.p}],
        tools=tools,
    )

    print("Response:", chat.choices[0])
    # Detect if tool_call
    if chat.choices[0].message.tool_calls:
        # Get the message from the first choice, then extract the first tool call from the tool_calls array
        completion_message = chat.choices[0].message.content
        print(completion_message)
        completion_first_tool = chat.choices[0].message.tool_calls[0]
        print(completion_first_tool)
        tool_name = completion_first_tool.function.name
        print(tool_name)
        tool_argument = json.loads(completion_first_tool.function.arguments)
        print(tool_argument)

        #  Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='

    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")

    print("Logs from your program will appear here!", file=sys.stderr)

    print(chat.choices[0].message.content)


if __name__ == "__main__":
    main()
