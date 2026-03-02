"""Entry point for the OpenDirectories MCP server."""

from .server import mcp


def main():
    """Run the MCP server."""
    mcp.run(transport='streamable-http')


if __name__ == '__main__':
    main()
