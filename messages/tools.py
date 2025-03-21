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
