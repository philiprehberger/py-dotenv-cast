# Changelog

## 0.1.0 (2026-03-21)

- Initial release
- Type-safe environment variable loading with `Env` class
- Casting methods: `str`, `int`, `float`, `bool`, `list`, `json`
- Boolean casting with support for common truthy/falsy strings
- `MissingEnvError` for required variables without defaults
- `load_dotenv` function for reading .env files
