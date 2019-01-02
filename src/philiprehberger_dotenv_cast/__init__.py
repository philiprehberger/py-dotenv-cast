"""Type-safe environment variable loading with casting and defaults."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

__all__ = [
    "Env",
    "MissingEnvError",
    "env",
    "load_dotenv",
]

_MISSING: Any = object()

_TRUE_VALUES = frozenset({"true", "1", "yes", "on"})
_FALSE_VALUES = frozenset({"false", "0", "no", "off"})


class MissingEnvError(KeyError):
    """Raised when a required environment variable is not set."""

    def __init__(self, key: str) -> None:
        super().__init__(key)
        self.key = key

    def __str__(self) -> str:
        return f"Missing required environment variable: {self.key}"


class Env:
    """Type-safe environment variable reader with casting."""

    def str(self, key: str, default: str = _MISSING) -> str:
        """Get an environment variable as a string.

        Args:
            key: Environment variable name.
            default: Default value if not set.

        Returns:
            The variable value as a string.

        Raises:
            MissingEnvError: If the variable is not set and no default is provided.
        """
        return self._get(key, default)

    def int(self, key: str, default: int = _MISSING) -> int:
        """Get an environment variable as an integer.

        Args:
            key: Environment variable name.
            default: Default value if not set.

        Returns:
            The variable value cast to int.

        Raises:
            MissingEnvError: If the variable is not set and no default is provided.
            ValueError: If the value cannot be cast to int.
        """
        raw = self._get_raw(key)
        if raw is _MISSING:
            if default is _MISSING:
                raise MissingEnvError(key)
            return default
        return int(raw)

    def float(self, key: str, default: float = _MISSING) -> float:
        """Get an environment variable as a float.

        Args:
            key: Environment variable name.
            default: Default value if not set.

        Returns:
            The variable value cast to float.

        Raises:
            MissingEnvError: If the variable is not set and no default is provided.
            ValueError: If the value cannot be cast to float.
        """
        raw = self._get_raw(key)
        if raw is _MISSING:
            if default is _MISSING:
                raise MissingEnvError(key)
            return default
        return float(raw)

    def bool(self, key: str, default: bool = _MISSING) -> bool:
        """Get an environment variable as a boolean.

        Truthy values: ``"true"``, ``"1"``, ``"yes"``, ``"on"`` (case-insensitive).
        Falsy values: ``"false"``, ``"0"``, ``"no"``, ``"off"`` (case-insensitive).

        Args:
            key: Environment variable name.
            default: Default value if not set.

        Returns:
            The variable value cast to bool.

        Raises:
            MissingEnvError: If the variable is not set and no default is provided.
            ValueError: If the value is not a recognized boolean string.
        """
        raw = self._get_raw(key)
        if raw is _MISSING:
            if default is _MISSING:
                raise MissingEnvError(key)
            return default
        lower = raw.lower()
        if lower in _TRUE_VALUES:
            return True
        if lower in _FALSE_VALUES:
            return False
        msg = f"Cannot cast {raw!r} to bool for {key}"
        raise ValueError(msg)

    def list(
        self,
        key: str,
        separator: str = ",",
        default: list[str] = _MISSING,
    ) -> list[str]:
        """Get an environment variable as a list of strings.

        Args:
            key: Environment variable name.
            separator: Delimiter to split on (default ``","``).
            default: Default value if not set.

        Returns:
            The variable value split into a list of stripped strings.

        Raises:
            MissingEnvError: If the variable is not set and no default is provided.
        """
        raw = self._get_raw(key)
        if raw is _MISSING:
            if default is _MISSING:
                raise MissingEnvError(key)
            return default
        return [item.strip() for item in raw.split(separator)]

    def json(self, key: str, default: Any = _MISSING) -> Any:
        """Get an environment variable parsed as JSON.

        Args:
            key: Environment variable name.
            default: Default value if not set.

        Returns:
            The parsed JSON value.

        Raises:
            MissingEnvError: If the variable is not set and no default is provided.
            json.JSONDecodeError: If the value is not valid JSON.
        """
        raw = self._get_raw(key)
        if raw is _MISSING:
            if default is _MISSING:
                raise MissingEnvError(key)
            return default
        return json.loads(raw)

    def _get_raw(self, key: str) -> Any:
        """Return the raw env value or ``_MISSING``."""
        value = os.environ.get(key)
        if value is None:
            return _MISSING
        return value

    def _get(self, key: str, default: Any) -> str:
        """Return the env value or default, raising if both are missing."""
        value = os.environ.get(key)
        if value is not None:
            return value
        if default is not _MISSING:
            return default
        raise MissingEnvError(key)


env = Env()


def load_dotenv(path: str = ".env") -> dict[str, str]:
    """Read a .env file and set variables in ``os.environ``.

    Lines starting with ``#`` and blank lines are ignored.
    Values may be optionally quoted with single or double quotes.

    Args:
        path: Path to the .env file (default ``".env"``).

    Returns:
        Dict of variables loaded from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    file_path = Path(path)
    if not file_path.is_file():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)

    loaded: dict[str, str] = {}
    text = file_path.read_text(encoding="utf-8")

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if "=" not in stripped:
            continue

        key, _, raw_value = stripped.partition("=")
        key = key.strip()
        raw_value = raw_value.strip()

        if (
            len(raw_value) >= 2
            and raw_value[0] == raw_value[-1]
            and raw_value[0] in ("'", '"')
        ):
            raw_value = raw_value[1:-1]

        os.environ[key] = raw_value
        loaded[key] = raw_value

    return loaded
