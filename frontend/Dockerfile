# Base image
FROM python:3.14-slim-trixie

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install dependencies
RUN uv sync

# Expose port
EXPOSE 5000

# Run the application
CMD ["uv", "run", "python", "app/__init__.py"]
