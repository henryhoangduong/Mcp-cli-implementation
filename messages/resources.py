from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from messages.send_message import send_message


async def send_resources_list(
    read_stream: MemoryObjectReceiveStream,
    write_stream: MemoryObjectSendStream,
) -> list:
    response = await send_message(
        read_stream=read_stream, write_stream=write_stream, method="resources/list"
    )
    return response.get("result", [])
