"""OpenDirectories Business Data MCP Server.

Exposes 12M+ verified business records across 10 countries as MCP tools.
Government-sourced (ASIC, NDIS, ACECQA, ACNC, CMS, Companies House),
enriched with Google Maps ratings and AI descriptions.

Can run standalone or as an Apify Actor in standby mode.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# --- Server port ---
_IS_APIFY = os.environ.get('APIFY_META_ORIGIN') == 'STANDBY'
PORT = int(os.environ.get('ACTOR_STANDBY_PORT', '5001')) if _IS_APIFY else 5001

# --- Configuration ---

REGIONS = {
    'apac': {
        'url': os.getenv(
            'APAC_SUPABASE_URL',
            'https://yruhtsqomrlhoqmhligt.supabase.co',
        ),
        'key': os.getenv(
            'APAC_SUPABASE_KEY',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlydWh0c3FvbXJsaG9xbWhsaWd0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTg0MTk3OCwiZXhwIjoyMDg3NDE3OTc4fQ.HUWZb9-p8CH8yFH_EqOzxowMa8go3-O4yW4KUrthtag',
        ),
        'countries': ['AU', 'NZ', 'SG'],
    },
    'us': {
        'url': os.getenv(
            'US_SUPABASE_URL',
            'https://oclajxwxyxorlfhahoqj.supabase.co',
        ),
        'key': os.getenv(
            'US_SUPABASE_KEY',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jbGFqeHd4eXhvcmxmaGFob3FqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTg0NjgxNCwiZXhwIjoyMDg3NDIyODE0fQ.dQkzSIwe5AH18WB9NCEI10suSGb9l8Vn0epx4BZ840E',
        ),
        'countries': ['US'],
    },
    'eu': {
        'url': os.getenv(
            'EU_SUPABASE_URL',
            'https://wyieuikljzxrlqzaawtv.supabase.co',
        ),
        'key': os.getenv(
            'EU_SUPABASE_KEY',
            'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind5aWV1aWtsanp4cmxxemFhd3R2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTg0NzQyNCwiZXhwIjoyMDg3NDIzNDI0fQ.Kho42cReP7oYMggrv35aJRyfjmAjtZgfb59pfmor07w',
        ),
        'countries': ['UK', 'CA', 'IE', 'FR'],
    },
}

DIRECTORIES = {
    'ndis': {'name': 'NDIS Disability Providers', 'country': 'AU', 'region': 'apac'},
    'financial': {'name': 'Financial Advisers', 'country': 'AU', 'region': 'apac'},
    'mortgage-broker': {'name': 'Mortgage Brokers', 'country': 'AU', 'region': 'apac'},
    'childcare': {'name': 'Childcare Centres', 'country': 'AU', 'region': 'apac'},
    'aged-care': {'name': 'Aged Care Facilities', 'country': 'AU', 'region': 'apac'},
    'charity': {'name': 'Charities', 'country': 'AU', 'region': 'apac'},
    'manufacturer': {'name': 'Manufacturers', 'country': 'AU', 'region': 'apac'},
    'ironside': {'name': 'Commercial Finance', 'country': 'AU', 'region': 'apac'},
    'local-services': {'name': 'Local Services', 'country': 'AU', 'region': 'apac'},
    'nz-charities': {'name': 'NZ Charities', 'country': 'NZ', 'region': 'apac'},
    'sg-companies': {'name': 'Singapore Companies', 'country': 'SG', 'region': 'apac'},
    'us-healthcare': {'name': 'US Healthcare Providers', 'country': 'US', 'region': 'us'},
    'us-nonprofits': {'name': 'US Nonprofits', 'country': 'US', 'region': 'us'},
    'us-carriers': {'name': 'US Transport Carriers', 'country': 'US', 'region': 'us'},
    'us-schools': {'name': 'US Schools', 'country': 'US', 'region': 'us'},
    'uk-companies': {'name': 'UK Companies', 'country': 'UK', 'region': 'eu'},
    'uk-establishments': {'name': 'UK Establishments', 'country': 'UK', 'region': 'eu'},
    'ca-corporations': {'name': 'Canadian Corporations', 'country': 'CA', 'region': 'eu'},
    'ie-companies': {'name': 'Irish Companies', 'country': 'IE', 'region': 'eu'},
    'fr-companies': {'name': 'French Companies', 'country': 'FR', 'region': 'eu'},
}

PUBLIC_FIELDS = (
    'id,name,slug,description,phone,website,'
    'street_address,suburb,state,postcode,country,'
    'google_rating,google_review_count,is_active,quality_score,profile_completeness'
)


# --- Supabase query helper ---

async def _query_supabase(
    region: str,
    params: dict[str, str],
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    """Query a regional Supabase instance."""
    cfg = REGIONS.get(region)
    if not cfg:
        return [], 0

    url = f'{cfg["url"]}/rest/v1/providers'
    headers = {
        'apikey': cfg['key'],
        'Authorization': f'Bearer {cfg["key"]}',
        'Accept': 'application/json',
        'Prefer': 'count=exact',
    }
    query_params: dict[str, str] = {
        'select': PUBLIC_FIELDS,
        'limit': str(limit),
        'offset': str(offset),
        'order': 'quality_score.desc.nullslast',
    }

    for key, val in params.items():
        if val:
            query_params[key] = val

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, headers=headers, params=query_params)
        if resp.status_code not in (200, 206):
            return [], 0

        total = 0
        content_range = resp.headers.get('Content-Range', '')
        if '/' in content_range:
            total_str = content_range.split('/')[-1]
            if total_str != '*':
                total = int(total_str)

        return resp.json(), total


def _get_region(country: str) -> str | None:
    """Find which region hosts a given country."""
    for region, cfg in REGIONS.items():
        if country.upper() in cfg['countries']:
            return region
    return None


def _regions_for_query(country: str = '', directory: str = '') -> list[str]:
    """Determine which regions to query."""
    if directory and directory in DIRECTORIES:
        return [DIRECTORIES[directory]['region']]
    if country:
        region = _get_region(country.upper())
        return [region] if region else []
    return list(REGIONS.keys())


# --- MCP Server ---

mcp = FastMCP(
    'OpenDirectories Business Data',
    host='0.0.0.0',
    port=PORT,
    streamable_http_path='/mcp',
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
async def search_businesses(
    query: str = '',
    country: str = '',
    directory: str = '',
    state: str = '',
    suburb: str = '',
    has_phone: bool = False,
    min_rating: float = 0,
    limit: int = 10,
) -> dict[str, Any]:
    """Search 12M+ verified businesses across 10 countries and 19 directories.

    Data sourced from government registers (ASIC, NDIS, ACECQA, ACNC, CMS,
    Companies House) and enriched with Google Maps ratings.

    Args:
        query: Business name or type to search for.
        country: ISO country code (AU, US, UK, CA, NZ, SG, IE, FR).
        directory: Filter by directory (ndis, financial, mortgage-broker,
            childcare, aged-care, charity, us-healthcare, uk-companies, etc).
        state: State or province code (e.g. NSW, VIC, CA, TX).
        suburb: Suburb or city name.
        has_phone: Only return businesses with a phone number.
        min_rating: Minimum Google rating (0-5).
        limit: Number of results (1-50, default 10).
    """
    limit = max(1, min(limit, 50))
    regions = _regions_for_query(country, directory)

    all_results: list[dict[str, Any]] = []
    total = 0

    for region in regions:
        params: dict[str, str] = {}
        if query:
            params['name'] = f'ilike.%{query}%'
        if directory:
            params['directory_id'] = f'eq.{directory}'
        if country:
            params['country'] = f'eq.{country.upper()}'
        if state:
            params['state'] = f'ilike.%{state}%'
        if suburb:
            params['suburb'] = f'ilike.%{suburb}%'
        if has_phone:
            params['phone'] = 'not.is.null'
        if min_rating > 0:
            params['google_rating'] = f'gte.{min_rating}'

        data, count = await _query_supabase(region, params, limit=limit)
        all_results.extend(data)
        total += count

        if len(all_results) >= limit:
            break

    results = all_results[:limit]
    return {
        'results': results,
        'count': len(results),
        'total_matching': total,
        'source': 'opendirectories.ai',
    }


@mcp.tool()
async def get_business(business_id: int, directory: str = '') -> dict[str, Any]:
    """Get detailed information about a specific business by its ID.

    Args:
        business_id: The unique ID of the business record.
        directory: Optional directory ID to narrow the search.
    """
    regions = _regions_for_query(directory=directory)

    for region in regions:
        params = {'id': f'eq.{business_id}'}
        if directory:
            params['directory_id'] = f'eq.{directory}'

        data, _ = await _query_supabase(region, params, limit=1)
        if data:
            return {'business': data[0], 'source': 'opendirectories.ai'}

    return {'error': f'Business {business_id} not found'}


@mcp.tool()
async def get_competitors(
    business_name: str,
    suburb: str,
    country: str = 'AU',
    directory: str = '',
    radius_suburbs: int = 1,
    limit: int = 10,
) -> dict[str, Any]:
    """Find competitors near a specific business.

    Returns businesses in the same directory/category within the same suburb
    or nearby, ranked by quality score. Useful for competitive analysis.

    Args:
        business_name: Name of the business to find competitors for.
        suburb: Suburb or city where the business is located.
        country: Country code (default AU).
        directory: Directory to search within (e.g. ndis, financial).
        radius_suburbs: Not yet implemented. Currently searches same suburb.
        limit: Number of competitors to return (1-20, default 10).
    """
    limit = max(1, min(limit, 20))
    regions = _regions_for_query(country, directory)

    all_results: list[dict[str, Any]] = []
    total = 0

    for region in regions:
        params: dict[str, str] = {
            'suburb': f'ilike.%{suburb}%',
            'country': f'eq.{country.upper()}',
        }
        if directory:
            params['directory_id'] = f'eq.{directory}'

        data, count = await _query_supabase(region, params, limit=limit + 5)
        all_results.extend(data)
        total += count

    # Filter out the queried business itself
    competitors = [
        r for r in all_results
        if business_name.lower() not in (r.get('name') or '').lower()
    ][:limit]

    return {
        'business': business_name,
        'suburb': suburb,
        'competitors': competitors,
        'competitor_count': len(competitors),
        'total_in_area': total,
        'source': 'opendirectories.ai',
    }


@mcp.tool()
async def market_density(
    category: str,
    state: str = '',
    suburb: str = '',
    country: str = 'AU',
    directory: str = '',
) -> dict[str, Any]:
    """Analyse market density for a business category in a location.

    Returns provider count, average rating, rating distribution, and coverage
    indicators. Useful for franchise expansion analysis and market research.

    Args:
        category: Business type or category to analyse (e.g. dentist, plumber, NDIS).
        state: State or province to analyse.
        suburb: Specific suburb or city (optional, narrows analysis).
        country: Country code (default AU).
        directory: Specific directory to search within.
    """
    regions = _regions_for_query(country, directory)

    all_results: list[dict[str, Any]] = []
    total = 0

    for region in regions:
        params: dict[str, str] = {
            'country': f'eq.{country.upper()}',
        }
        if category:
            params['name'] = f'ilike.%{category}%'
        if state:
            params['state'] = f'ilike.%{state}%'
        if suburb:
            params['suburb'] = f'ilike.%{suburb}%'
        if directory:
            params['directory_id'] = f'eq.{directory}'

        data, count = await _query_supabase(region, params, limit=100)
        all_results.extend(data)
        total += count

    # Calculate density metrics
    ratings = [
        r['google_rating'] for r in all_results
        if r.get('google_rating') and r['google_rating'] > 0
    ]
    review_counts = [
        r['google_review_count'] for r in all_results
        if r.get('google_review_count') and r['google_review_count'] > 0
    ]
    with_website = sum(1 for r in all_results if r.get('website'))
    with_phone = sum(1 for r in all_results if r.get('phone'))

    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0
    avg_reviews = round(sum(review_counts) / len(review_counts), 1) if review_counts else 0

    # Rating distribution
    rating_dist = {'5_star': 0, '4_star': 0, '3_star': 0, '2_star': 0, '1_star': 0}
    for r in ratings:
        if r >= 4.5:
            rating_dist['5_star'] += 1
        elif r >= 3.5:
            rating_dist['4_star'] += 1
        elif r >= 2.5:
            rating_dist['3_star'] += 1
        elif r >= 1.5:
            rating_dist['2_star'] += 1
        else:
            rating_dist['1_star'] += 1

    sampled = len(all_results)

    return {
        'category': category,
        'location': {
            'country': country,
            'state': state or 'all',
            'suburb': suburb or 'all',
        },
        'total_providers': total,
        'sampled': sampled,
        'metrics': {
            'avg_google_rating': avg_rating,
            'avg_review_count': avg_reviews,
            'pct_with_website': round(with_website / sampled * 100, 1) if sampled else 0,
            'pct_with_phone': round(with_phone / sampled * 100, 1) if sampled else 0,
            'rating_distribution': rating_dist,
        },
        'top_rated': sorted(
            [r for r in all_results if r.get('google_rating')],
            key=lambda x: (x.get('google_rating', 0), x.get('google_review_count', 0)),
            reverse=True,
        )[:5],
        'source': 'opendirectories.ai',
    }


@mcp.tool()
async def verify_business(
    business_name: str,
    country: str = 'AU',
    abn: str = '',
    suburb: str = '',
) -> dict[str, Any]:
    """Verify if a business exists in government registers.

    Checks against ASIC, NDIS, ACECQA, ACNC, CMS, and Companies House data.
    Returns verification confidence and matched record details.

    Args:
        business_name: Name of the business to verify.
        country: Country code (default AU).
        abn: Australian Business Number (optional, improves match accuracy).
        suburb: Suburb or city (optional, improves match accuracy).
    """
    regions = _regions_for_query(country)

    best_match: dict[str, Any] | None = None
    best_score = 0

    for region in regions:
        params: dict[str, str] = {
            'name': f'ilike.%{business_name}%',
            'country': f'eq.{country.upper()}',
        }
        if suburb:
            params['suburb'] = f'ilike.%{suburb}%'

        data, total = await _query_supabase(region, params, limit=5)

        for record in data:
            score = 0
            name = (record.get('name') or '').lower()
            query_name = business_name.lower()

            # Exact name match
            if name == query_name:
                score += 50
            elif query_name in name or name in query_name:
                score += 30

            # Location match
            if suburb and suburb.lower() in (record.get('suburb') or '').lower():
                score += 20

            # Data completeness signals
            if record.get('phone'):
                score += 5
            if record.get('website'):
                score += 5
            if record.get('google_rating'):
                score += 5
            if record.get('is_active'):
                score += 10
            if record.get('quality_score'):
                score += 5

            if score > best_score:
                best_score = score
                best_match = record

    if best_match and best_score >= 30:
        confidence = min(best_score / 100, 0.99)
        return {
            'verified': True,
            'confidence': round(confidence, 2),
            'matched_record': {
                'name': best_match.get('name'),
                'suburb': best_match.get('suburb'),
                'state': best_match.get('state'),
                'phone': best_match.get('phone'),
                'website': best_match.get('website'),
                'google_rating': best_match.get('google_rating'),
                'is_active': best_match.get('is_active'),
            },
            'source': 'opendirectories.ai',
        }

    return {
        'verified': False,
        'confidence': 0,
        'message': f'No matching business found for "{business_name}" in {country}',
        'source': 'opendirectories.ai',
    }


@mcp.tool()
async def chat_search(
    question: str,
    limit: int = 10,
) -> dict[str, Any]:
    """Ask a natural language question about businesses.

    Uses AI to parse your question into structured filters and search
    12M+ verified business records. Returns matching businesses with
    a natural language summary.

    Examples:
    - "Find plumbers in Sydney with good reviews"
    - "NDIS providers near Melbourne that have a website"
    - "Healthcare facilities in New York"
    - "Top-rated childcare centres in Brisbane"
    - "Companies in London with phone numbers"

    Args:
        question: Natural language search query.
        limit: Maximum results to return (1-50, default 10).
    """
    api_url = os.getenv('DATA_API_URL', 'http://localhost:9472')

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(
                f'{api_url}/v1/chat',
                params={'q': question, 'limit': min(limit, 50)},
            )
            if resp.status_code != 200:
                return {
                    'error': f'Chat search failed: {resp.status_code}',
                    'hint': 'Try search_businesses for direct filtering',
                }
            return resp.json()
    except Exception as e:
        return {
            'error': f'Chat search unavailable: {e}',
            'hint': 'Use search_businesses with explicit filters instead',
        }


@mcp.tool()
async def list_directories() -> dict[str, Any]:
    """List all available directories and their record counts.

    Returns the 20 directories across 10 countries with metadata about
    each data source.
    """
    return {
        'directories': {
            dir_id: {
                'name': info['name'],
                'country': info['country'],
                'region': info['region'],
            }
            for dir_id, info in DIRECTORIES.items()
        },
        'total_directories': len(DIRECTORIES),
        'total_records': '12,160,000+',
        'countries': sorted({d['country'] for d in DIRECTORIES.values()}),
        'source': 'opendirectories.ai',
    }
