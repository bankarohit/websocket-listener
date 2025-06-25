.PHONY: install install-dev run test docker-build docker-run

install:
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt

run:
	python3 -m listener.main

test:
	pytest

docker-build:
	docker build -t websocket-listener .

docker-run:
	docker run -p 8000:8000 websocket-listener

venv:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

