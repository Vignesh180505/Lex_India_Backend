# LexIndia — AI-Powered Indian Legal Access Platform

LexIndia enables any citizen to describe a legal problem in plain language (English, Tamil, or Hindi) and receive a structured list of applicable Indian laws, simplified explanations, and direct links to official court filing portals.

## Architecture

| Layer              | Technology                                                    |
|--------------------|---------------------------------------------------------------|
| Frontend           | Next.js 14 (App Router), Tailwind CSS, shadcn/ui, i18next     |
| Backend API        | FastAPI (Python 3.11)                                         |
| Text Generation    | OpenAI GPT-4o (simplification + translation)                  |
| Embedding Model    | sentence-transformers/all-MiniLM-L6-v2 (384-dim vectors)     |
| Vector Database    | pgvector extension on PostgreSQL 15                           |
| Cache              | Redis 7                                                       |
| Scraping           | Playwright (async), BeautifulSoup4                            |
| Task Queue         | Celery + Redis                                                |
| Containerisation   | Docker + Docker Compose                                       |

## Quick Start

```bash
# 1. Clone and configure
cp backend/.env.example backend/.env
# Edit backend/.env with your OPENAI_API_KEY

# 2. Start all services
docker compose up -d

# 3. Start frontend
cd frontend && npm install && npm run dev
```

## Project Structure

See the full repository structure in the project brief documentation.

## License

MIT
