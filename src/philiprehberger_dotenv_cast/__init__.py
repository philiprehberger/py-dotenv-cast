"""Type-safe environment variable loading with casting and defaults."""

from __future__ import annotations

import json
import os
import re
from datetime import timedelta
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

_BYTE_UNITS: dict[str, int] = {
    "": 1,
    "b": 1,
    "k": 1024,
    "kb": 1024,
    "kib": 1024,
    "m": 1024**2,
    "mb": 1024**2,
    "mib": 1024**2,
    "g": 1024**3,
    "gb": 1024**3,
    "gib": 1024**3,
    "t": 1024**4,
    "tb": 1024**4,
    "tib": 1024**4,
}

_DURATION_UNITS: dict[str, float] = {
    "ms": 0.001,
    "s": 1.0,
    "m": 60.0,
    "h": 3600.0,
    "d": 86400.0,
    "w": 604800.0,
}

_BYTE_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z]*)\s*$")
_DURATION_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)([a-zA-Z]+)")


def _parse_bytes(raw: str) -> int:
    match = _BYTE_RE.match(raw)
    if not match:
        msg = f"Cannot parse byte size from {raw!r}"
        raise ValueError(msg)
    number, unit = match.groups()
    unit = unit.lower()
    if unit not in _BYTE_UNITS:
        msg = f"Unknown byte unit {unit!r} in {raw!r}"
        raise ValueError(msg)
    return int(float(number) * _BYTE_UNITS[unit])


def _parse_duration(raw: str) -> timedelta:
    cleaned = raw.replace(" ", "")
    if not cleaned:
        msg = f"Cannot parse duration from {raw!r}"
        raise ValueError(msg)

    matches = list(_DURATION_RE.finditer(cleaned))
    if not matches or "".join(m.group(0) for m in matches) != cleaned:
        msg = f"Cannot parse duration from {raw!r}"
        raise ValueError(msg)

    total = 0.0
    for match in matches:
        number, unit = match.groups()
        unit = unit.lower()
        if unit not in _DURATION_UNITS:
            msg = f"Unknown duration unit {unit!r} in {raw!r}"
            raise ValueError(msg)
        total += float(number) * _DURATION_UNITS[unit]
    return timedelta(seconds=total)


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

    def url(self, key: str, default: str = _MISSING) -> str:
        """Get an environment variable as a validated URL.

        Args:
            key: Environment variable name.
            default: Default value if not set.

        Returns:
            The variable value validated as a URL.

        Raises:
            MissingEnvError: If the variable is not set and no default is provided.
            ValueError: If the value does not start with http:// or https://.
        """
        value = self._get(key, default)
        if not value.startswith(("http://", "https://")):
            msg = f"Invalid URL for {key}: {value}"
            raise ValueError(msg)
        return value

    def path(self, key: str, default: str = _MISSING) -> Path:
        """Get an environment variable as a Path object.

        Args:
            key: Environment variable name.
            default: Default value if not set.

        Returns:
            The variable value as a Path.

        Raises:
            MissingEnvError: If the variable is not set and no default is provided.
        """
        return Path(self._get(key, default))

    def bytes(self, key: str, default: int = _MISSING) -> int:
        """Get an environment variable parsed as a byte count.

        Accepts plain integers (``"4096"``) or human-readable size strings
        with a unit suffix: ``"512KB"``, ``"2.5MB"``, ``"1GiB"``. Suffixes
        are case-insensitive, ``KB`` and ``KiB`` both mean 1024 bytes.

        Args:
            key: Environment variable name.
            default: Default value if not set (in raw bytes).

        Returns:
            The variable value parsed as an integer number of bytes.

        Raises:
            MissingEnvError: If the variable is not set and no default is provided.
            ValueError: If the value cannot be parsed.
        """
        raw = self._get_raw(key)
        if raw is _MISSING:
            if default is _MISSING:
                raise MissingEnvError(key)
            return default
        return _parse_bytes(raw)

    def duration(self, key: str, default: timedelta | None = _MISSING) -> timedelta:
        """Get an environment variable parsed as a :class:`~datetime.timedelta`.

        Accepts duration strings made up of one or more number+unit segments:
        ``"30s"``, ``"5m"``, ``"1h30m"``, ``"500ms"``, ``"1d12h"``. Recognized
        units: ``ms``, ``s``, ``m``, ``h``, ``d``, ``w``.

        Args:
            key: Environment variable name.
            default: Default value if not set.

        Returns:
            The variable value parsed as a ``timedelta``.

        Raises:
            MissingEnvError: If the variable is not set and no default is provided.
            ValueError: If the value cannot be parsed.
        """
        raw = self._get_raw(key)
        if raw is _MISSING:
            if default is _MISSING:
                raise MissingEnvError(key)
            return default  # type: ignore[return-value]
        return _parse_duration(raw)

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
