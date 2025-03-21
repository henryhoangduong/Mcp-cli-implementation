import json
import sys
import logging
from messages.send_initialize_message import send_initialize
from messages.send_ping_message import send_ping
import anyio.streams
from stdio_server_parameters import StdioServerParameters
import anyio
from config import load_config
from stdio_server_shutdown import shutdown_stdio_server
import stdio_client
import argparse
from stdio_client import get_default_environment, stdio_client

DEFAULT_CONFIG = "server_config.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)


async def main(config_path: str, server_name: str) -> None:
    process = None
    read_stream = None
    write_stream = None
    try:
        print("Starting server process .... ", file=sys.stderr)
        server_params = await load_config(config_path, server_name)
        process = await anyio.open_process(
            [server_params.command, *server_params.args],
            env=server_params.env or get_default_environment(),
            stdin=True,
            stdout=True,
            stderr=sys.stderr,
        )

        async with stdio_client(server_params) as (read_stream, write_stream):

            init_result = await send_initialize(read_stream, write_stream)
            if not init_result:
                print(f"Server initialization failed", file=sys.stderr)
                return
            print("Pinging Server...")
            result = await send_ping(read_stream, write_stream)

            # check the result
            if result is True:
                # success
                print("Server is up and running", file=sys.stderr)
            else:
                # failed
                print("Server ping failed", file=sys.stderr)

        # complete
        print("Shutting Down....", file=sys.stderr)
    except KeyboardInterrupt:
        print("KeyboardInterrupt recieved, initiating shutdown", file=sys.stderr)
    except Exception as e:
        print(f"Error in main: {e}", file=sys.stderr)
    finally:
        await shutdown_stdio_server(read_stream, write_stream, process)


if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description="MCP Ping Client")
    parser.add_argument(
        "--config-file",
        default=DEFAULT_CONFIG,
        help="Path to JSON configration file containing server details.",
    )
    # get the server name
    parser.add_argument(
        "--server",
        required=True,
        help="Name of the server configuration to use from the config file.",
    )
    args = parser.parse_args()
    try:
        anyio.run(main, args.config_file, args.server)
    except:
        print("KeyboardInterrupt detected, exiting cleanly", file=sys.stderr)
