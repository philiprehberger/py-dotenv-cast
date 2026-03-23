# philiprehberger-dotenv-cast

[![Tests](https://github.com/philiprehberger/py-dotenv-cast/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-dotenv-cast/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-dotenv-cast.svg)](https://pypi.org/project/philiprehberger-dotenv-cast/)
[![License](https://img.shields.io/github/license/philiprehberger/py-dotenv-cast)](LICENSE)

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
| `load_dotenv(path?)` | Load a .env file into `os.environ` |
| `Env` | Class for creating custom instances |
| `MissingEnvError` | Raised when a required variable is missing |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
