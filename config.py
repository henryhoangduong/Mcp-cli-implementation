import json
import sys
import logging
from stdio_server_parameters import StdioServerParameters

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)


async def load_config(config_path: str, server_name: str) -> StdioServerParameters:
    try:
        logging.debug(f"Loading config from {config_path}")
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        server_config = config.get("mcpServers", {}).get(server_name)
        if not server_config:
            error_msg = f"Server '{server_name}' not found in configuration file."
            logging.error(error_msg)
            raise ValueError(error_msg)
        result = StdioServerParameters(
            command=server_config["command"],
            args=server_config.get("args", []),
            env=server_config.get("env"),
        )
        logging.debug(
            f"Loaded config: command='{result.command}', args={result.args}, env={result.env}"
        )
        return result
    except FileNotFoundError:
        error_msg = f"Configuration file not found: {config_path}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in configuration file: {e.msg}"
        logging.error(error_msg)
        raise json.JSONDecodeError(error_msg, e.doc, e.pos)
    except ValueError as e:
        logging.error(str(e))
        raise
