import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
TOKEN_FILE = PROJECT_ROOT / ".env"

ENV_VARS = {
    "cmc": "CMC_TOKEN",
    "bot": "BOT_TOKEN",
    "mistral": "MISTRAL_TOKEN",
    "fmp": "FMP_TOKEN",
}

_file_tokens = None


def load_file_tokens():
    global _file_tokens

    if _file_tokens is None:
        _file_tokens = {}
        if not TOKEN_FILE.exists():
            raise RuntimeError("Missing .env file")
        for line in TOKEN_FILE.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            _file_tokens[key.strip()] = value.strip()

    return _file_tokens


def get_token(service):
    variable = ENV_VARS.get(service)
    if variable is None:
        return ""

    return os.environ.get(variable) or load_file_tokens().get(variable, "")
