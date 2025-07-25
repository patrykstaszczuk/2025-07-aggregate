init:
	if [ ! -d ".venv" ]; then python -m venv .venv; fi
	.venv/bin/pip install -r requirements.txt
	pre-commit install
