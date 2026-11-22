# Contributing to AetherNet

Thanks for contributing to AetherNet.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Checks Before Opening a PR

```bash
pytest -q
ruff check .
```

- Keep the explicit authorization gate intact for active network/pentest tooling.
- Never commit `.env` or local `logs/` audit files.
