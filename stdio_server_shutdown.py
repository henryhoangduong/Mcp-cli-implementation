import logging
import anyio
import anyio.abc
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from typing import Optional
from stdio_server_parameters import StdioServerParameters
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)


async def shutdown_stdio_server(
    read_stream: Optional[MemoryObjectReceiveStream],
    write_stream: Optional[MemoryObjectSendStream],
    process: anyio.abc.Process,
    timeout: float = 5.0,
) -> None:
    logging.info("Initializing stdio shutdown")
    try:
        if process.stdin:
            await process.stdin.aclose()
            logging.info("Process exited normally")
        with anyio.fail_after(timeout):
            await process.wait()
            logging.info("Process exited normally")
            return
    except TimeoutError:
        logging.warning(
            f"Server did not exit within {timeout} seconds, sending SIGTERM"
        )
        process.terminate()
        try:
            with anyio.fail_after(timeout):
                await process.terminate()
                logging.info("Process exited after SIGTERM")
        except TimeoutError:
            logging.warning("Server did not respond to SIGTERM, sending SIGKILL")
            process.kill()

            await process.wait()
            logging.info("Process exited after SIGKILL")
    except Exception as e:
        logging.error(f"Unexpected error during stdio server shutdown: {e}")
        process.kill()
        await process.wait()
        logging.info("Process forcibly terminated")
    finally:
        logging.info("Stdio server shutdown complete")
