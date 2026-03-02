# Installing OpenDirectories MCP Server

## Claude Desktop / Cline / Cursor

Add this to your MCP client configuration:

### Option A: Hosted (recommended — zero setup)

```json
{
  "mcpServers": {
    "opendirectories": {
      "url": "https://secure-wave--opendirectories-business-data.apify.actor/mcp"
    }
  }
}
```

### Option B: Self-hosted via PyPI

```bash
pip install opendirectories-mcp
```

Then add to your config:

```json
{
  "mcpServers": {
    "opendirectories": {
      "command": "opendirectories-mcp",
      "env": {
        "APAC_SUPABASE_URL": "your-url",
        "APAC_SUPABASE_KEY": "your-anon-key",
        "US_SUPABASE_URL": "your-url",
        "US_SUPABASE_KEY": "your-anon-key",
        "EU_SUPABASE_URL": "your-url",
        "EU_SUPABASE_KEY": "your-anon-key"
      }
    }
  }
}
```

### Option C: Docker

```json
{
  "mcpServers": {
    "opendirectories": {
      "command": "docker",
      "args": ["run", "-p", "5001:5001", "ghcr.io/bigjai/opendirectories-mcp"]
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `search_businesses` | Search 12M+ businesses by name, country, directory, location, rating |
| `get_business` | Get full details for a specific business by ID |
| `get_competitors` | Find competitors near a business location |
| `market_density` | Analyse market saturation for a category in a location |
| `verify_business` | Verify a business against government registers |
| `list_directories` | List all 19 directories with metadata |
