"""
Naukri Job Search MCP Server

Wraps the Apify muhammetakkurtt/naukri-job-scraper actor.
Provides tools to Claude for searching and inspecting Naukri job postings.
"""

import html
import logging
import os
import re
import sys
from typing import Any, Dict, List, Literal, Optional
from dotenv import load_dotenv
import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# ─── Setup Logging to stderr (Never stdout for stdio MCP) ──────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("naukri_mcp")

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
if not APIFY_API_TOKEN:
    logger.warning("APIFY_API_TOKEN is not set. API calls will fail.")

ACTOR_ID = "alpcnRV9YI9lYVPWk"
APIFY_RUN_URL = f"https://api.apify.com/v2/acts/{ACTOR_ID}/run-sync-get-dataset-items"

# ─── City Name → Naukri City ID Mapping ───────────────────────────────────────

CITY_IDS = {
    "mumbai": "134", "bombay": "134", "navi mumbai": "138", "thane": "323", "mumbai suburban": "135",
    "bengaluru": "97", "bangalore": "97",
    "delhi": "382", "new delhi": "6", "delhi/ncr": "9508", "delhi / ncr": "9508", "ncr": "9508",
    "gurugram": "73", "gurgaon": "73", "noida": "220", "greater noida": "350", "faridabad": "72", "ghaziabad": "213",
    "pune": "139", "hyderabad": "17", "chennai": "183", "kolkata": "232",
    "ahmedabad": "51", "surat": "64", "vadodara": "65", "jaipur": "173",
    "lucknow": "216", "kanpur": "215", "indore": "125", "bhopal": "123",
    "chandigarh": "4", "mohali": "167", "coimbatore": "184", "kochi": "110", "ernakulam": "111",
    "thiruvananthapuram": "120", "trivandrum": "120", "nagpur": "136", "nashik": "137",
    "visakhapatnam": "26", "vizag": "26", "bhubaneswar": "155", "goa": "45",
    "mangaluru": "105", "mangalore": "105", "mysuru": "106", "mysore": "106",
    "dehradun": "224", "guwahati": "33", "ludhiana": "166", "amritsar": "162",
    "patna": "38", "ranchi": "94", "jamshedpur": "93", "raipur": "43", "vijayawada": "25",
}


def resolve_city_id(name: str) -> Optional[str]:
    """Case-insensitive city-name to Naukri city ID lookup."""
    if not name:
        return None
    return CITY_IDS.get(name.strip().lower())


def clean_html(raw_html: str) -> str:
    """Convert common HTML structures to clean markdown/plain text."""
    if not raw_html:
        return "N/A"
    text = html.unescape(raw_html)
    # Replace line breaks and paragraph ends
    text = re.sub(r"<(br|br/|br\s*/)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div)>", "\n\n", text, flags=re.IGNORECASE)
    # Convert lists to markdown bullets
    text = re.sub(r"<li[^>]*>", "\n- ", text, flags=re.IGNORECASE)
    # Strip all remaining tags
    text = re.sub(r"<[^>]+>", "", text)
    # Normalize excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ─── MCP Server Init & Shared HTTP Client ─────────────────────────────────────

mcp = FastMCP("naukri_mcp")

# Reusable client for connection pooling
_http_client: Optional[httpx.AsyncClient] = None

def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=120.0)
    return _http_client


async def call_apify(payload: dict) -> List[Dict[str, Any]]:
    """Calls the Apify actor synchronously and returns dataset items."""
    if not APIFY_API_TOKEN:
        raise ValueError("APIFY_API_TOKEN not configured. Please set it in your .env file.")

    client = get_http_client()
    response = await client.post(
        APIFY_RUN_URL,
        params={"token": APIFY_API_TOKEN},
        json=payload,
    )
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, list) else []


def handle_error(e: Exception) -> str:
    """Consistent, actionable error messages for the LLM."""
    if isinstance(e, httpx.HTTPStatusError):
        code = e.response.status_code
        if code == 401:
            return "Error: Invalid Apify API token. Verify APIFY_API_TOKEN in .env."
        if code == 429:
            return "Error: Apify rate limit reached. Please wait a moment and try again."
        return f"Error: Apify API returned HTTP {code}: {e.response.text[:300]}"
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The scraping actor took longer than 120s to respond."
    return f"Error ({type(e).__name__}): {str(e)}"


def format_job_summary(job: dict) -> str:
    """Formats search result items."""
    return "\n".join([
        f"**{job.get('title') or 'N/A'}** at {job.get('companyName') or 'N/A'}",
        f"  Location   : {job.get('location') or 'N/A'}",
        f"  Experience : {job.get('experience') or 'N/A'}",
        f"  Salary     : {job.get('salary') or 'Not disclosed'}",
        f"  Skills     : {job.get('tagsAndSkills') or 'N/A'}",
        f"  Posted     : {job.get('footerPlaceholderLabel') or 'N/A'}",
        f"  Job ID     : {job.get('jobId') or 'N/A'}",
        f"  URL        : {job.get('jdURL') or 'N/A'}",
    ])


# ─── MCP Resource: Supported Cities ───────────────────────────────────────────

@mcp.resource("naukri://cities")
def list_supported_cities() -> str:
    """Provides a list of standard Indian cities mapped to Naukri IDs."""
    return ", ".join(sorted(set(CITY_IDS.keys())))


# ─── Tool 1: Search Jobs ──────────────────────────────────────────────────────

@mcp.tool(
    name="naukri_search_jobs",
    description="Search Naukri.com for job postings by keyword, location, experience, and freshness.",
)
async def naukri_search_jobs(
    keyword: str = Field(..., description="Job title, tech stack, or skill (e.g. 'Python Developer', 'Data Scientist')"),
    location: Optional[str] = Field(default=None, description="City name (e.g. 'Bangalore', 'Mumbai', 'Pune'). Leave blank for all India."),
    max_jobs: int = Field(default=10, ge=1, le=50, description="Number of jobs to return (1-50). Default is 10."),
    freshness_days: Literal["1", "3", "7", "15", "30", "all"] = Field(default="7", description="Filter jobs posted within N days."),
    experience_years: Optional[int] = Field(default=None, ge=0, le=35, description="Years of experience (e.g. 0 for freshers, 3, 5)."),
    sort_by: Literal["date", "relevance"] = Field(default="date", description="Sort order: 'date' for newest first, 'relevance' for closest match."),
) -> str:
    payload: Dict[str, Any] = {
        "keyword": keyword,
        "maxJobs": max(max_jobs, 50),  # Apify actor minimum constraint
        "fetchDetails": False,
        "freshness": freshness_days,
        "sortBy": sort_by,
    }

    if experience_years is not None:
        payload["experience"] = str(experience_years)

    unknown_city_notice = ""
    if location:
        city_id = resolve_city_id(location)
        if city_id:
            payload["cities"] = [city_id]
        else:
            payload["keyword"] = f"{keyword} {location}"
            unknown_city_notice = f"\n_Note: '{location}' not found in city ID map; appended to keyword._\n"

    try:
        jobs = await call_apify(payload)
    except Exception as e:
        return handle_error(e)

    if not jobs:
        return f"No jobs found for keyword '{keyword}'. Try removing filters or using broader search terms.{unknown_city_notice}"

    selected_jobs = jobs[:max_jobs]
    formatted = [format_job_summary(j) for j in selected_jobs]
    header = f"Found {len(selected_jobs)} jobs for '{keyword}':{unknown_city_notice}\n\n"
    return header + "\n\n---\n\n".join(formatted)


# ─── Tool 2: Get Job Details ──────────────────────────────────────────────────

@mcp.tool(
    name="naukri_get_job_details",
    description="Fetch full details for a specific Naukri job ID including description, skills, and company reviews.",
)
async def naukri_get_job_details(
    job_id: str = Field(..., description="Naukri Job ID (e.g. '220126040161') obtained from search."),
) -> str:
    payload = {
        "jobIds": [job_id.strip()],
        "fetchDetails": True,
        "maxJobs": 1,
    }

    try:
        jobs = await call_apify(payload)
    except Exception as e:
        return handle_error(e)

    if not jobs:
        return f"No job found with ID '{job_id}'. Please verify the ID."

    job = jobs[0]

    # Safe nested dictionary extraction (guards against null values)
    details = job.get("jobDetails") or {}
    company = details.get("companyDetail") or {}
    skills = details.get("keySkills") or {}
    salary = details.get("salaryDetail") or {}
    ambition = job.get("ambitionBoxDetails") or {}
    reviews = ambition.get("reviews") or []
    locations = details.get("locations") or []

    preferred_skills = [s.get("label", "") for s in (skills.get("preferred") or []) if s.get("label")]
    other_skills = [s.get("label", "") for s in (skills.get("other") or []) if s.get("label")]
    all_skills = ", ".join(preferred_skills + other_skills) or "Not specified"

    location_str = ", ".join(loc.get("label", "") for loc in locations if loc.get("label")) or job.get("location") or "N/A"

    raw_description = details.get("description") or "No description provided."
    clean_description = clean_html(raw_description)

    lines = [
        f"# {details.get('title') or job.get('title') or 'N/A'}",
        f"**Company**: {company.get('name') or job.get('companyName') or 'N/A'}",
        f"**Location**: {location_str}",
        f"**Experience**: {details.get('experienceText') or job.get('experience') or 'N/A'}",
        f"**Employment Type**: {details.get('employmentType') or 'N/A'}",
        f"**Salary**: {salary.get('label') or job.get('salary') or 'Not disclosed'}",
        f"**Work Mode**: {details.get('wfhLabel') or 'Office'}",
        "",
        "## Required Skills",
        all_skills,
        "",
        "## About the Company",
        company.get("details") or "N/A",
        "",
        "## Job Description",
        clean_description,
    ]

    if reviews:
        lines.append("\n## Employee Reviews (via AmbitionBox)")
        for r in reviews[:2]:
            title = r.get("Title") or "Review"
            likes = (r.get("LikesText") or "").strip()
            lines.append(f"- **{title}**: {likes[:200]}..." if likes else f"- **{title}**")

    return "\n".join(lines)


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()