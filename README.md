# philiprehberger-dotenv-cast

[![Tests](https://github.com/philiprehberger/py-dotenv-cast/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-dotenv-cast/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-dotenv-cast.svg)](https://pypi.org/project/philiprehberger-dotenv-cast/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-dotenv-cast)](https://github.com/philiprehberger/py-dotenv-cast/commits/main)

Type-safe environment variable loading with casting and defaults.

## Installation

```bash
pip install philiprehberger-dotenv-cast
```

## Usage

```python
from philiprehberger_dotenv_cast import env, load_dotenv

# Load a .env file into os.environ
load_dotenv()

# Read variables with type casting
host = env.str("HOST", "localhost")
port = env.int("PORT", 8080)
debug = env.bool("DEBUG", False)
tags = env.list("TAGS")  # "a,b,c" -> ["a", "b", "c"]
```

### Boolean Casting

Boolean values are case-insensitive:

- Truthy: `"true"`, `"1"`, `"yes"`, `"on"`
- Falsy: `"false"`, `"0"`, `"no"`, `"off"`

### List Splitting

```python
# Default separator is ","
tags = env.list("TAGS")  # "a, b, c" -> ["a", "b", "c"]

# Custom separator
paths = env.list("PATHS", separator=":")
```

### JSON Parsing

```python
config = env.json("CONFIG")  # '{"key": "value"}' -> {"key": "value"}
```

### Byte Sizes

Parse human-readable size strings into raw byte counts:

```python
max_upload = env.bytes("MAX_UPLOAD")     # "10MB"  -> 10 * 1024**2
buffer = env.bytes("BUFFER", default=4096)  # "1.5KiB" -> 1536
```

Supported suffixes (case-insensitive): `B`, `KB`/`KiB`, `MB`/`MiB`, `GB`/`GiB`, `TB`/`TiB`. A bare number is treated as bytes.

### Durations

Parse duration strings into `datetime.timedelta` values:

```python
from datetime import timedelta

timeout = env.duration("TIMEOUT")           # "30s"     -> timedelta(seconds=30)
poll = env.duration("POLL_INTERVAL")        # "500ms"   -> timedelta(milliseconds=500)
ttl = env.duration("CACHE_TTL", default=timedelta(minutes=5))  # "1h30m" -> 1h30m
```

Supported units (lowercase): `ms`, `s`, `m`, `h`, `d`, `w`. Compound durations (`1h30m`) are summed.

### Missing Variables

Variables without a default raise `MissingEnvError`:

```python
from philiprehberger_dotenv_cast import env, MissingEnvError

try:
    secret = env.str("SECRET_KEY")  # raises if not set
except MissingEnvError:
    print("SECRET_KEY is required")
```

### Loading .env Files

```python
from philiprehberger_dotenv_cast import load_dotenv

# Load default .env
load_dotenv()

# Load a specific file
load_dotenv("config/.env.production")
```

## API

| Method / Function | Description |
|-------------------|-------------|
| `env.str(key, default?)` | Get variable as string |
| `env.int(key, default?)` | Get variable cast to int |
| `env.float(key, default?)` | Get variable cast to float |
| `env.bool(key, default?)` | Get variable cast to bool |
| `env.list(key, separator?, default?)` | Get variable split into a list |
| `env.json(key, default?)` | Get variable parsed as JSON |
| `env.bytes(key, default?)` | Get variable parsed as a byte size (`512KB`, `2MiB`, …) |
| `env.duration(key, default?)` | Get variable parsed as a `timedelta` (`30s`, `1h30m`, …) |
| `load_dotenv(path?)` | Load a .env file into `os.environ` |
| `Env` | Class for creating custom instances |
| `MissingEnvError` | Raised when a required variable is missing |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-dotenv-cast)

🐛 [Report issues](https://github.com/philiprehberger/py-dotenv-cast/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-dotenv-cast/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
