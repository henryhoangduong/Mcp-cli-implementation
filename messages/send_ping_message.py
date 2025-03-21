import logging
import anyio
from messages.json_rpc_message import JSONRPCMessage
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream


async def send_ping(
    read_stream: MemoryObjectReceiveStream,
    write_stream: MemoryObjectSendStream,
) -> bool:
    message = JSONRPCMessage(id="ping-1", method="ping")
    logging.debug("Send ping message")

    await write_stream.send(message)
    try:
        with anyio.fail_after(5):
            async for response in read_stream:
                if isinstance(response, Exception):
                    logging.error(f"Error proceessing init result: {e}")
                    continue
                logging.debug(f"Server Response: {response.model_dump()}")
                return True

    except TimeoutError:
        logging.error("Timeout waiting for ping response")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during ping: {e}")
        return False
    logging.error("Initialization response timeout")
    return None
