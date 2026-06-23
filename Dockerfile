# Stage 1: build the frontend
FROM node:22-slim AS frontend-build
WORKDIR /build
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build && node generate-index.mjs

# Stage 2: Python backend that serves the frontend static files
FROM python:3.12-slim
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install Python dependencies (separate layer for caching)
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

# Copy backend source code
COPY backend/ .

# Copy frontend static assets produced by Stage 1
COPY --from=frontend-build /build/dist/client ./static

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
