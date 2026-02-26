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

    messages = [{"role": "user", "content": args.p}]

    while True:
        chat = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=tools,
        )

        print("Voici Chat:")
        print(chat.model_dump(exclude_none=True))

        if not chat.choices[0].message.tool_calls:
            break

        message_assistant = chat.choices[0].message
        messages.append(message_assistant.model_dump())

        for tool_call in message_assistant.tool_calls or []:
            tool_args = json.loads(tool_call.function.arguments)

            if tool_call.function.name == "Read":
                with open(tool_args["file_path"], "r") as f:
                    file_content = f.read()

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": file_content,
                    }
                )

    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")

    print("Logs from your program will appear here!", file=sys.stderr)

    if not chat.choices[0].message.tool_calls:
        print(chat.choices[0].message.content)


if __name__ == "__main__":
    main()
