import logging
import anyio
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from messages import json_rpc_message
from messages.json_rpc_message import JSONRPCMessage


async def send_message(
    read_stream: MemoryObjectReceiveStream,
    write_stream: MemoryObjectSendStream,
    method: str,
    params: dict = None,
    timeout: float = 5,
    message_id: str = None,
    retries: int = 3,
) -> dict:
    message = JSONRPCMessage(id=message_id or method, method=method, params=params)
    for attempt in range(1, retries + 1):
        try:
            logging.debug(f"Attempt {attempt}/{retries}: Sending message: {message}")
            await write_stream.send(message)
            with anyio.fail_after(5):
                async for response in read_stream:
                    if not isinstance(response, Exception):
                        logging.debug(f"Received response: {response.model_dump()}")
                        return response.model_dump()
                    else:
                        logging.error(f"Server error: {response}")
                        raise response
        except TimeoutError:
            logging.error(
                f"Timeout waiting for response to method '{method}' (Attempt {attempt}/{retries})"
            )
            if attempt == retries:
                raise
        except Exception as e:
            logging.error(
                f"Unexpected error during '{method}' request: {e} (Attempt {attempt}/{retries})"
            )
            if attempt == retries:
                raise
        await anyio.sleep(2)
