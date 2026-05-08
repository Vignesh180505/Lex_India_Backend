# LexIndia Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright, PostgreSQL, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=600 -r requirements.txt

# Install Playwright browsers (Chromium only for scraping)
RUN playwright install chromium --with-deps

# Copy application code
COPY . .

# Create data and log directories
RUN mkdir -p data/urls logs

# Expose port
EXPOSE 7860

# Startup script: run Alembic migrations then start uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 7860"]
