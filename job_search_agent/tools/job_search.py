import os
import time
from typing import Dict, List, Optional

import json
import requests


def _search_with_jsearch(profile: Dict, location: Optional[str], remote: Optional[bool]) -> List[Dict]:
    api_key = os.getenv("RAPIDAPI_JSEARCH_KEY")
    if not api_key:
        return []
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    }
    skills = ", ".join((profile or {}).get("skills", [])[:10])
    roles = ", ".join((profile or {}).get("preferred_roles", [])[:5])
    query = roles or skills or "software engineer"
    params = {"query": query}
    if location:
        params["location"] = location
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        data = resp.json()
        results = data.get("data") or data.get("results") or []
        jobs = []
        for it in results:
            jobs.append(
                {
                    "id": it.get("job_id") or it.get("id"),
                    "title": it.get("job_title"),
                    "company": it.get("employer_name") or it.get("company"),
                    "location": it.get("job_city") or it.get("location"),
                    "remote": it.get("job_is_remote"),
                    "posted_at": it.get("job_posted_at_datetime_utc") or it.get("posted_at"),
                    "salary": it.get("job_min_salary"),
                    "url": it.get("job_apply_link") or it.get("job_google_link") or it.get("job_link"),
                    "source": "jsearch",
                    "raw": it,
                }
            )
        if remote is True:
            jobs = [j for j in jobs if j.get("remote") is True]
        return jobs
    except Exception:
        return []


def _search_with_serpapi(profile: Dict, location: Optional[str], remote: Optional[bool]) -> List[Dict]:
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        return []
    url = "https://serpapi.com/search.json"
    skills = ", ".join((profile or {}).get("skills", [])[:10])
    roles = ", ".join((profile or {}).get("preferred_roles", [])[:5])
    query = roles or skills or "software engineer"
    params = {
        "engine": "google_jobs",
        "q": query,
        "api_key": api_key,
    }
    if location:
        params["location"] = location
    try:
        resp = requests.get(url, params=params, timeout=20)
        data = resp.json()
        results = (data.get("jobs_results") or [])
        jobs = []
        for it in results:
            jobs.append(
                {
                    "id": it.get("job_id") or it.get("job_id_token") or it.get("job_id_o"),
                    "title": it.get("title"),
                    "company": it.get("company_name") or it.get("company"),
                    "location": it.get("location"),
                    "remote": "remote" in (it.get("location") or "").lower(),
                    "posted_at": it.get("detected_extensions", {}).get("posted_at"),
                    "salary": it.get("detected_extensions", {}).get("salary"),
                    "url": it.get("share_link") or it.get("link"),
                    "source": "serpapi",
                    "raw": it,
                }
            )
        if remote is True:
            jobs = [j for j in jobs if j.get("remote") is True]
        return jobs
    except Exception:
        return []


def _serpapi_web_site_search(site: str, query: str, location: Optional[str]) -> List[Dict]:
    # Disabled per requirement to use Playwright MCP for job search
    return []


def _search_linkedin(profile: Dict, location: Optional[str], remote: Optional[bool]) -> List[Dict]:
    skills = ", ".join((profile or {}).get("skills", [])[:8])
    roles = ", ".join((profile or {}).get("preferred_roles", [])[:5])
    base_query = roles or skills or "software engineer"
    if remote is True:
        base_query += " remote"
    return _serpapi_web_site_search("linkedin.com/jobs", base_query, location)


def _search_naukri(profile: Dict, location: Optional[str], remote: Optional[bool]) -> List[Dict]:
    skills = ", ".join((profile or {}).get("skills", [])[:8])
    roles = ", ".join((profile or {}).get("preferred_roles", [])[:5])
    base_query = roles or skills or "software engineer"
    if remote is True:
        base_query += " remote"
    return _serpapi_web_site_search("naukri.com", base_query, location)


def _search_wellfound(profile: Dict, location: Optional[str], remote: Optional[bool]) -> List[Dict]:
    skills = ", ".join((profile or {}).get("skills", [])[:8])
    roles = ", ".join((profile or {}).get("preferred_roles", [])[:5])
    base_query = roles or skills or "software engineer"
    if remote is True:
        base_query += " remote"
    return _serpapi_web_site_search("wellfound.com", base_query, location)


def search_jobs(profile_json: str, location: Optional[str] = None, remote: Optional[bool] = None) -> Dict:
    """Search across integrated sources using available API keys.

    Env support: RAPIDAPI_JSEARCH_KEY, SERPAPI_KEY

    Args:
        profile_json: JSON string of profile dict from extract_profile.profile
        location: Optional user-preferred location string
        remote: Optional flag to filter remote-only results

    Returns:
        dict: { status, sources_used, jobs: [ { id, title, company, location, remote, posted_at, salary, url, source } ] }
    """
    try:
        profile: Dict = json.loads(profile_json) if profile_json else {}
    except Exception:
        profile = {}

    sources_used: List[str] = []
    jobs: List[Dict] = []

    jsearch_jobs = _search_with_jsearch(profile or {}, location, remote)
    if jsearch_jobs:
        sources_used.append("jsearch")
        jobs.extend(jsearch_jobs)

    serpapi_jobs = _search_with_serpapi(profile or {}, location, remote)
    if serpapi_jobs:
        sources_used.append("serpapi_google_jobs")
        jobs.extend(serpapi_jobs)

    # Site-specific searches via SerpAPI Web with site filters
    # Site searches will be performed via Playwright MCP tools at runtime by the LLM;
    # this function remains as a fallback aggregator when browsing is unavailable.

    # Deduplicate by URL or title+company
    dedup: Dict[str, Dict] = {}
    for j in jobs:
        key = j.get("url") or f"{j.get('title')}::{j.get('company')}"
        dedup[key] = j
    deduped = list(dedup.values())

    return {
        "status": "success",
        "sources_used": sources_used,
        "jobs": deduped,
        "meta": {"count": len(deduped), "location": location, "remote_only": bool(remote)},
    }


