.PHONY: dev setup test seed migrate lint docker-up docker-down e2e clean

# ── One-command dev setup ──
setup:
	@echo "🔧 Setting up CyberShield AI..."
	cd apps/api-gateway && pip install -r requirements.txt
	cd apps/web && npm install
	@echo "✅ Setup complete. Run 'make dev' to start."

# ── Start all services (local) ──
dev:
	@echo "🚀 Starting CyberShield AI..."
	cd apps/api-gateway && uvicorn main:app --reload --port 8000 &
	cd apps/web && npm run dev &
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "📡 API: http://localhost:8000/docs"

# ── Run all tests ──
test:
	@echo "🧪 Running backend tests..."
	cd apps/api-gateway && python -m pytest tests/ -v --tb=short
	@echo "🧪 Running frontend lint..."
	cd apps/web && npm run lint

# ── Lint ──
lint:
	cd apps/web && npm run lint
	cd apps/api-gateway && python -m flake8 --max-line-length=120 --exclude=migrations,__pycache__ . || true

# ── Database ──
migrate:
	cd apps/api-gateway && alembic upgrade head

seed:
	cd apps/api-gateway && python -m data.seed_db

# ── Docker ──
docker-up:
	docker compose -f infra/docker-compose.yml up --build

docker-down:
	docker compose -f infra/docker-compose.yml down -v

docker-prod:
	docker compose -f infra/docker-compose.yml -f infra/docker-compose.prod.yml up --build -d

# ── E2E tests ──
e2e:
	cd tests/e2e && npx playwright install --with-deps chromium
	cd tests/e2e && npx playwright test

# ── Clean ──
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf apps/api-gateway/dev*.db 2>/dev/null || true
	@echo "🧹 Cleaned."