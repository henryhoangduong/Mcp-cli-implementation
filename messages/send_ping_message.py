import logging
import anyio
from messages.json_rpc_message import JSONRPCMessage
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from messages.send_message import send_message


async def send_ping(
    read_stream: MemoryObjectReceiveStream,
    write_stream: MemoryObjectSendStream,
) -> bool:
    """Send a ping message to the server and log the response."""
    response = await send_message(
        read_stream=read_stream,
        write_stream=write_stream,
        method="ping",
        message_id="ping-1",
    )
    return response is not None
