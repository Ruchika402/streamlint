.PHONY: dev test up

dev:
	@echo "Starting backend and frontend..."
	cd backend && . .venv/bin/activate && python manage.py runserver & cd frontend && npm run dev

test:
	@echo "Running backend tests..."
	cd backend && . .venv/bin/activate && ruff check . && pytest
	@echo "Building frontend..."
	cd frontend && npm run build

up:
	@echo "Starting Docker Compose..."
	docker compose up --build