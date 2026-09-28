# Use a slim Python image
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install the project and its dependencies
# We use --system to install into the system Python environment in the container
RUN uv pip install --system .

# Install the stdio-to-HTTP bridge
RUN uv pip install --system "mcp-proxy==0.9.0"

# Expose port 8080 (default for Cloud Run)
EXPOSE 8080

# Wrap the existing entrypoint with mcp-proxy instead of running it directly
CMD ["mcp-proxy", "--port", "8080", "--sse-path", "/sse", "--", "google-ads-mcp"]
