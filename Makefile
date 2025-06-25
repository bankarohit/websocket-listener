.PHONY: install run test docker-build docker-run

install:
	pip install -r requirements.txt

run:
	python -m listener.main

test:
	pytest

docker-build:
	docker build -t websocket-listener .

docker-run:
	docker run -p 8000:8000 websocket-listener

venv:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

