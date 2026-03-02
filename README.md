<!-- mcp-name: io.github.BigJai/opendirectories-business-data -->

# OpenDirectories MCP Server

Search **12M+ verified businesses** across **10 countries** and **19 directories** via the Model Context Protocol.

All data sourced from government registers and enriched with Google Maps ratings and AI descriptions.

## Quick Start

### Hosted (zero setup)

Add to your MCP client config (Claude Desktop, Cline, Cursor, etc.):

```json
{
  "mcpServers": {
    "opendirectories": {
      "url": "https://secure-wave--opendirectories-business-data.apify.actor/mcp"
    }
  }
}
```

### Install via PyPI

```bash
pip install opendirectories-mcp
```

```json
{
  "mcpServers": {
    "opendirectories": {
      "command": "opendirectories-mcp",
      "env": {
        "APAC_SUPABASE_URL": "https://your-instance.supabase.co",
        "APAC_SUPABASE_KEY": "your-anon-key",
        "US_SUPABASE_URL": "https://your-instance.supabase.co",
        "US_SUPABASE_KEY": "your-anon-key",
        "EU_SUPABASE_URL": "https://your-instance.supabase.co",
        "EU_SUPABASE_KEY": "your-anon-key"
      }
    }
  }
}
```

## Tools

### `search_businesses`

Search across all records with rich filters.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Business name or type |
| `country` | string | ISO code: AU, US, UK, CA, NZ, SG, IE, FR |
| `directory` | string | Directory ID (see `list_directories`) |
| `state` | string | State/province code (e.g. NSW, CA, TX) |
| `suburb` | string | Suburb or city name |
| `has_phone` | bool | Only businesses with phone numbers |
| `min_rating` | float | Minimum Google rating (0-5) |
| `limit` | int | Results to return (1-50, default 10) |

### `get_business`

Get full details for a business by its ID.

| Parameter | Type | Description |
|-----------|------|-------------|
| `business_id` | int | Unique business record ID |
| `directory` | string | Optional directory to narrow search |

### `get_competitors`

Find competitors near a business location, ranked by quality score.

| Parameter | Type | Description |
|-----------|------|-------------|
| `business_name` | string | Business to find competitors for |
| `suburb` | string | Suburb or city |
| `country` | string | Country code (default AU) |
| `directory` | string | Directory to search within |
| `limit` | int | Results (1-20, default 10) |

### `market_density`

Analyse market saturation with rating distributions, digital presence metrics, and top-rated providers.

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Business type (e.g. dentist, plumber) |
| `state` | string | State or province |
| `suburb` | string | Suburb or city |
| `country` | string | Country code (default AU) |
| `directory` | string | Directory to search within |

### `verify_business`

Verify a business against government registers with confidence scoring.

| Parameter | Type | Description |
|-----------|------|-------------|
| `business_name` | string | Business name to verify |
| `country` | string | Country code (default AU) |
| `abn` | string | Australian Business Number (optional) |
| `suburb` | string | Suburb (optional, improves accuracy) |

### `list_directories`

Returns all 19 directories with country and region metadata. No parameters.

## Data Sources

| Region | Source | Directories |
|--------|--------|-------------|
| Australia | ASIC, NDIS, ACECQA, ACNC | Financial advisers, mortgage brokers, childcare, aged care, charities, manufacturers, disability providers, commercial finance, local services |
| United States | CMS, IRS | Healthcare providers, nonprofits, transport, education |
| United Kingdom | Companies House | UK companies |
| Canada | National register | Canadian businesses |
| New Zealand | Charities Commission | NZ charities |
| Singapore | ACRA | Singapore companies |
| Ireland | CRO | Irish charities |
| France | INSEE | French enterprises |

## Coverage

- **12,160,000+** verified business records
- **19** specialised directories
- **10** countries (AU, US, UK, CA, NZ, SG, IE, FR + growing)
- **3** regional databases (APAC, US, EU)
- Google Maps ratings and review counts
- AI-generated business descriptions

## Use Cases

- **Lead generation** — Find businesses by category, location, and quality score
- **Competitive analysis** — Map competitors in any suburb or city
- **Market research** — Analyse density, ratings, and digital presence
- **Business verification (KYB)** — Verify against government registers
- **Franchise expansion** — Identify underserved markets

## Self-Hosting

Set environment variables for your Supabase instances:

```bash
export APAC_SUPABASE_URL=https://your-instance.supabase.co
export APAC_SUPABASE_KEY=your-anon-key
export US_SUPABASE_URL=https://your-instance.supabase.co
export US_SUPABASE_KEY=your-anon-key
export EU_SUPABASE_URL=https://your-instance.supabase.co
export EU_SUPABASE_KEY=your-anon-key
export PORT=5001

opendirectories-mcp
```

Or use Docker:

```bash
docker run -p 5001:5001 \
  -e APAC_SUPABASE_URL=... \
  -e APAC_SUPABASE_KEY=... \
  ghcr.io/bigjai/opendirectories-mcp
```

## License

MIT
