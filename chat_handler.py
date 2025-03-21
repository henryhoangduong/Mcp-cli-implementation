import os
import ollama
from openai import OpenAI
from system_prompt_generator import SystemPromptGenerator
from dotenv import load_dotenv
from messages.tools import send_tools_list

load_dotenv()

if not os.getenv("OPEN_AI_KEY"):
    raise ValueError("The OPEN_AI_KEY environment variable is not set")


async def handle_chat_mode(read_stream, write_stream):
    """Enter chat mode with the system prompt"""
    try:
        print("\nFetching tools for chat mode")
        tools = await send_tools_list(read_stream, write_stream)
        if not tools:
            print(f"Failed to fetch tools. Exiting chat mode.")
            return
        prompt_generator = SystemPromptGenerator()
        tools_json = {"tools": tools}
        sytem_prompt = prompt_generator.generate_prompt(tools_json)
        client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
        print("\nEntering chat mode. Type 'exit' to quit.")
        while True:
            user_message = input("\nYou: ").strip()
            if user_message.lower() in ["exit", "quti"]:
                print("Exiting chat mode.")
                break
            messages = [
                {"role": "system", "content": sytem_prompt},
                {"role": "system", "content": user_message},
            ]
            completion = client.chat.completions.create(
                model="gpt-4o-mini", messages=messages
            )
            response_content = completion.choices[0].message.content
            print("Assistant: ", response_content)
    except Exception as e:
        print(f"\nError in chat mode: {e}")
