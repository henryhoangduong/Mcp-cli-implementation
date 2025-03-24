import json
import os
from openai import OpenAI
from system_prompt_generator import SystemPromptGenerator
from dotenv import load_dotenv
from messages.tools import send_tools_list, call_tool

load_dotenv()

if not os.getenv("OPEN_AI_KEY"):
    raise ValueError("The OPEN_AI_KEY environment variable is not set")


async def handle_chat_mode(read_stream, write_stream):
    """Enter chat mode with the multi-call support for autonomous tool chaining"""
    try:
        print("\nFetching tools for chat mode")
        # Fetch tools dynamically
        tools_response = await send_tools_list(read_stream, write_stream)

        # Extract tools list
        tools = tools_response.get("tools", [])
        if not isinstance(tools, list) or not all(
            isinstance(tool, dict) for tool in tools
        ):
            print(f"Invalid tools format recieved. Expected a list of dictionaries")
            return

        # Generate system prompt with CoT
        prompt_generator = SystemPromptGenerator()
        tools_json = {"tools": tools}
        system_prompt = prompt_generator.generate_prompt(tools_json)
        system_prompt += "\nReason step-by-step. If multiple steps are needed, call tools iteratively to achieve the goal.  if you are unsure the schema of data sources, you can check if there is a tool to describe a data source"
        client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
        print("\nEntering chat mode. Type 'exit' to quit.")
        openai_tools = [
            {
                type: "function",
                "function": {
                    "name": tool["name"],
                    "parameters": tool.get("inputSchema", {}),
                },
            }
            for tool in tools
        ]

        # Debugging: Print OpenAI tools configuration
        print("Configured OpenAI tools: ", openai_tools)
        conversation_history = [{"role": "system", "content": system_prompt}]
        while True:
            user_message = input("\nYou: ").strip()
            if user_message.lower() in ["exit", "quti"]:
                print("Exiting chat mode.")
                break
            # Add user message to conversation history
            while True:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=conversation_history,
                    tools=openai_tools,
                )

                # Access the response or tool call 
                response_message  = completion.choices[0].message
                if hasattr(response_message, "tool_calls") and response_message.tool_calls:

                    # Debugging: print the tool call response
                    print("Tool call response: ",response_message.tool_calls)
                    
                    for tool_call in response_message.tool_calls:
                        tool_name = tool_call.function.name
                        raw_arguments = tool_call.function.arguments
                        try:
                            tool_args  = json.loads(raw_arguments) if raw_arguments else {}
                        except json.JSONDecodeError:
                            print(f"Error decoding arguments for tool '{tool_name}': {raw_arguments}")
                            continue
                        print(f"\nTools '{tool_name}' invoked arguments: {tool_args}")

                        # Call the tool using provided arguments
                        tool_response = await call_tool(tool_name, tool_args, read_stream, write_stream)
                        if tool_response.get("isError"):
                            print(f"Error calling tool: {tool_response.get("error")}")
                            break

                        # Process and format tool reponse
                        response_content = tool_response.get("content",[])
                        formatted_response = ""
                        if isinstance(response_content, list):
                            for item in response_content:
                                if item.get("type") == "text":
                                    formatted_response += item.get("text", "No content") + "\n"
                        else:
                            formatted_response = str(response_content)

                else:
                     # Handle normal assistant response
                     response_content = response_message.content
                     print("Assistant:", response_content)
                     conversation_history.append({"role": "assistant", "content": response_content})
                     break

    except Exception as e:
        print(f"\nError in chat mode: {e}")
