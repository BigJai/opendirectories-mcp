FROM python:3.13-slim

LABEL org.opencontainers.image.source="https://github.com/BigJai/opendirectories-mcp"
LABEL org.opencontainers.image.description="OpenDirectories Business Data MCP Server"
LABEL io.modelcontextprotocol.server.name="opendirectories-business-data"

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src/ src/

RUN pip install --no-cache-dir .

ENV PORT=5001

EXPOSE ${PORT}

CMD ["python", "-m", "opendirectories_mcp"]
