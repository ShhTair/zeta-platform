.PHONY: help install dev setup db-up db-down db-reset migrate test clean

help:
	@echo "ZETA Platform API - Available Commands"
	@echo "======================================"
	@echo "make install      - Install dependencies"
	@echo "make dev          - Run development server"
	@echo "make setup        - Full setup (db + migrations + admin)"
	@echo "make db-up        - Start database containers"
	@echo "make db-down      - Stop database containers"
	@echo "make db-reset     - Reset database"
	@echo "make migrate      - Run database migrations"
	@echo "make test         - Run tests"
	@echo "make clean        - Clean up temp files"

install:
	python3.12 -m venv venv || python3.11 -m venv venv || python3 -m venv venv
	./venv/bin/pip install --upgrade pip setuptools wheel
	./venv/bin/pip install -r requirements.txt
	@echo "✓ Dependencies installed"

dev:
	./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

setup: db-up
	@sleep 3
	./venv/bin/alembic upgrade head
	./venv/bin/python init_db.py

db-up:
	docker-compose up -d
	@echo "✓ Database containers started"

db-down:
	docker-compose down
	@echo "✓ Database containers stopped"

db-reset: db-down
	docker-compose down -v
	docker-compose up -d
	@sleep 3
	./venv/bin/alembic upgrade head
	@echo "✓ Database reset complete"

migrate:
	./venv/bin/alembic upgrade head
	@echo "✓ Migrations applied"

test:
	./venv/bin/pytest -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	@echo "✓ Cleaned up temporary files"
