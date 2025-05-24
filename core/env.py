import os
import re

from core.utils import fail


def load_dotenv(path=".env"):
    if not os.path.exists(path):
        fail(f".env file not found at {path}")
        return

    env_vars = {}
    with open(path, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            try:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                env_vars[key] = value
            except ValueError:
                fail(f"Invalid line in .env: {line}")

    def replacer(match):
        var_name = match.group(1)
        return env_vars.get(var_name, os.environ.get(var_name, ""))

    for key in list(env_vars.keys()):
        original_value = env_vars[key]
        expanded_value = re.sub(r"\$\{([^}]+)}", replacer, original_value)
        while expanded_value != original_value:
            original_value = expanded_value
            expanded_value = re.sub(r"\$\{([^}]+)}", replacer, original_value)
        env_vars[key] = expanded_value
        os.environ[key] = expanded_value


def parse_runner_settings(env_var_value):
    settings = {}
    if not env_var_value:
        return settings

    for pair in env_var_value.split(","):
        key, value = pair.split("=", 1)
        settings[key.strip()] = value.strip().lower()
    return settings
