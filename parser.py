from typing import Any
import re


def config_parser(file: str) -> dict[str, Any]:
    """Read a config file into a dictionary of raw string values.

    Blank lines and lines starting with '#' are ignored. Each remaining
    line must contain a '=' separating a key from its value.

    Args:
        file: Path to the configuration file.

    Returns:
        A dict mapping each key to its raw (unconverted) string value.

    Raises:
        ValueError: If a line has no '=' or a key is duplicated.
    """

    data: dict[str, str] = {}
    with open(file, "r", encoding="utf-8-sig") as f:
        for line in f:
            clean_line = line.strip()
            if not clean_line or clean_line.startswith("#"):
                continue
            if "=" in clean_line:
                k, v = clean_line.split("=", 1)
                key = k.strip()
                value = v.strip()

                if key in data:
                    raise ValueError(f"Duplicate key: '{k}'")
                data[key] = value
            else:
                raise ValueError(
                    "[ERROR] Invalid format. Config must have '='"
                    )
    return data


def converter(data: dict[str, Any]) -> dict[str, Any]:
    """Convert raw string values into their proper types.

    WIDTH and HEIGHT become ints, ENTRY and EXIT become (x, y) tuples,
    PERFECT becomes a bool, and SEED becomes an int. Unknown keys are
    rejected.

    Args:
        data: The dict of raw string values from config_parser.

    Returns:
        The same dict with values converted to their real types.

    Raises:
        ValueError: If a value has the wrong format or the key is unknown.
    """

    for key, value in data.items():
        if key in ["WIDTH", "HEIGHT"]:
            try:
                data[key] = int(value)
            except ValueError:
                raise ValueError(f"'{key}' must be an integer. Got: '{value}'")

        elif key in ["ENTRY", "EXIT"]:
            try:
                x, y = value.split(",")
                x = int(x)
                y = int(y)
                data[key] = (x, y)
            except ValueError:
                raise ValueError(
                    f"'{key}' must be an integer in 'x,y' format. "
                    f"Got: '{value}'")

        elif key == "OUTPUT_FILE":
            pass

        elif key == "PERFECT":
            clean_value = value.lower()
            if clean_value in ["true", "1"]:
                data[key] = True
            elif clean_value in ["false", "0"]:
                data[key] = False
            else:
                raise ValueError(
                    f"'PERFECT' must be True or False. "
                    f"Got: '{value}'"
                    )

        elif key == "SEED":
            try:
                data[key] = int(value)
            except ValueError:
                raise ValueError(f"'SEED' must be an integer. Got: '{value}'")

        else:
            raise ValueError(f"Unknown configuration key: '{key}'")

    return data


def config_validator(data: dict[str, Any], config_file: str) -> bool:
    """Validate that the converted config values make sense.

    Checks that all required keys are present, that ENTRY and EXIT are
    within bounds and not equal, that WIDTH and HEIGHT are within the
    allowed range, and that OUTPUT_FILE is a safe file name that does
    not overwrite a protected file.

    Args:
        data: The converted config dict.
        config_file: Name of the input config file, protected from
            being overwritten by OUTPUT_FILE.

    Returns:
        True if every value is valid.

    Raises:
        KeyError: If a required key is missing.
        ValueError: If any value is invalid or unsafe.
    """

    required = ["ENTRY", "EXIT", "WIDTH", "HEIGHT", "OUTPUT_FILE", "PERFECT"]
    for key in required:
        if key not in data:
            raise KeyError("Missing required argument in default_config.txt")

    for key, value in data.items():
        if key in ["ENTRY", "EXIT"]:
            if data["ENTRY"] == data["EXIT"]:
                raise ValueError(
                    "ENTRY and EXIT positions cannot be the same!"
                    )

            x, y = value
            if x < 0 or y < 0 or x >= (data["WIDTH"]) or y >= (data["HEIGHT"]):
                raise ValueError(
                    "[WARNING] Coordinates for 'ENTRY'/'EXIT'"
                    " are out of maze bounds!"
                    )

        elif key in ["WIDTH", "HEIGHT"]:
            if (
                data["WIDTH"] > 52 or data["WIDTH"] < 5
                or data["HEIGHT"] > 24
                or data["HEIGHT"] < 5
            ):
                raise ValueError(
                    "[WARNING] Invalid dimensions: "
                    "WIDTH must be 5-52 and HEIGHT 5-24. "
                    )

        elif key == "OUTPUT_FILE":
            protected = {"requirements.txt", "config.txt", config_file}
            if not re.fullmatch(r"[A-Za-z0-9_-]+\.txt", value):
                raise ValueError(
                    "OUTPUT_FILE must be a simple name ending in '.txt' "
                    "(letters, digits, '_' or '-'). Got: '" + value + "'"
                )
            if value in protected:
                raise ValueError(
                    "OUTPUT_FILE cannot overwrite a protected file: '"
                    + value + "'")

    return True
