from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from messages.send_message import send_message


async def send_tools_list(
    read_stream: MemoryObjectReceiveStream, write_stream: MemoryObjectSendStream
) -> list:
    """Send a 'tools/list' message and return the list of tools."""
    resposne = await send_message(
        read_stream=read_stream,
        write_stream=write_stream,
        method="tools/list",
    )
    return resposne.get("result", [])


async def call_tool(
    tool_name: str,
    arguments: dict,
    read_stream: MemoryObjectReceiveStream,
    write_stream: MemoryObjectSendStream,
) -> dict:
    """Send a 'tools/call' request and return the tool's response."""
    try:
        response = (
            await send_message(
                read_stream=read_stream,
                write_stream=write_stream,
                method="tools/call",
                params={"name": tool_name, "arguments": arguments},
            ),
        )
    except Exception as e:
        return {"isError": True, "error": str(e)}
