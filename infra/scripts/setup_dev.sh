#!/bin/bash
# ═══════════════════════════════════════════
# One-command dev environment setup
# ═══════════════════════════════════════════

set -e

CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
NC='\033[0m'

echo -e "${CYAN}🛡️  Setting up CyberShield AI development environment${NC}"
echo ""

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required. Install from https://docker.com"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3.11+ is required."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js 20+ is required."; exit 1; }

echo -e "${GREEN}✅ Prerequisites found${NC}"

# Environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}📝 Created .env from .env.example — edit with your values${NC}"
fi

# Create upload directory
mkdir -p /tmp/cybershield_uploads

# Start database
echo -e "${YELLOW}🗄️  Starting PostgreSQL...${NC}"
docker compose up -d db
sleep 4

# Backend setup
echo -e "${YELLOW}🐍 Setting up Python backend...${NC}"
cd apps/api-gateway
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate 2>/dev/null || true
pip install -r requirements.txt -q

# Run migrations
echo -e "${YELLOW}📊 Running database migrations...${NC}"
alembic upgrade head

# Seed data
echo -e "${YELLOW}🌱 Seeding database...${NC}"
python -m data.seed_db

cd ../..

# Frontend setup
echo -e "${YELLOW}⚛️  Setting up Next.js frontend...${NC}"
cd apps/web
npm install
cd ../..

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "Run ${CYAN}make dev${NC} to start all services"
echo ""
echo -e "  🌐 Frontend:  http://localhost:3000"
echo -e "  🔌 API Docs:  http://localhost:8000/docs"
echo -e "  🗄️  Database:  localhost:5432"