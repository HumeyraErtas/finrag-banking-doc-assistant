.PHONY: venv install ingest api demo test lint docker-up docker-down docker-up-ollama

venv:
	python -m venv .venv

install:
	. .venv/bin/activate && pip install -r requirements.txt

ingest:
	. .venv/bin/activate && python scripts/ingest_cli.py

api:
	. .venv/bin/activate && uvicorn api.main:app --reload --port 8000

demo:
	. .venv/bin/activate && streamlit run streamlit_app.py

test:
	. .venv/bin/activate && pytest -q

docker-up:
	docker compose up --build

docker-up-ollama:
	docker compose --profile ollama up --build

docker-down:
	docker compose down
