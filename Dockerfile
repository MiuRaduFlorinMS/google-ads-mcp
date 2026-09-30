# Use a slim Python image
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install google-ads-mcp into an ISOLATED venv so its mcp==2.0.0 / fastmcp>=4
# cannot be clobbered by mcp-proxy's older mcp pin.
RUN uv venv /app/venv
RUN uv pip install --python /app/venv/bin/python .

# Install the stdio-to-HTTP bridge in the separate system environment.
RUN uv pip install --system "mcp-proxy==0.9.0"

# Expose port 8080 (default for Cloud Run)
EXPOSE 8080

# mcp-proxy runs the google-ads-mcp binary FROM THE VENV as a stdio subprocess.
# The subprocess inherits Cloud Run env vars (GOOGLE_ADS_*), so auth still works.
CMD ["mcp-proxy", "--transport", "sse", "--port", "8080", "--host", "0.0.0.0", "--", "/app/venv/bin/google-ads-mcp"]
