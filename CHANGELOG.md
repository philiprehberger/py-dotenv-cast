# Changelog


## 0.2.0 (2026-04-04)

- Add `Env.url()` for validated URL loading
- Add `Env.path()` for Path object loading
## 0.1.2 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility
- Add GitHub issue templates, dependabot config, and PR template

## 0.1.1 (2026-03-22)

- Add Development section to README
- Add Changelog URL to project URLs
- Add `#readme` anchor to Homepage URL
- Add pytest and mypy configuration

## 0.1.0 (2026-03-21)

- Initial release
- Type-safe environment variable loading with `Env` class
- Casting methods: `str`, `int`, `float`, `bool`, `list`, `json`
- Boolean casting with support for common truthy/falsy strings
- `MissingEnvError` for required variables without defaults
- `load_dotenv` function for reading .env files
