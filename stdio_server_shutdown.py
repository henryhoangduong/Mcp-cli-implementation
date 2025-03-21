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
        if process:
            if process.stdin:
                await process.stdin.aclose()
                logging.info("Closed stdin stream")
        with anyio.fail_after(timeout):
            await process.wait()
            logging.info("Process exited normally")
            return
    except TimeoutError:
        logging.warning(
            f"Server did not exist within {timeout} seconds, sending SIGTERM"
        )
        if process:
            process.terminate()
        try:
            with anyio.fail_after(timeout):
                await process.wait()
                logging.info("Process exited after SIGTERM")
                return
        except TimeoutError:
            logging.warning("Server did not respond to SIGTERM, sending SIGKILL")
            # ensure we have a process
            if process:
                # kill
                process.kill()

                # Step 4: Wait for the process to terminate after SIGKILL
                await process.wait()
                logging.info("Process exited after SIGKILL")
    except Exception as e:
        logging.error(f"Unexpected error during stdio server shutdown: {e}")
        if process:
            process.kill()
            await process.wait()
            logging.info("Process forcibly terminated")
    finally:
        # complete
        logging.info("Stdio server shutdown complete")
