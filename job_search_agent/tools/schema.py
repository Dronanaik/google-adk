from typing import Dict, List
import json


def format_results(profile_result_json: str, search_result_json: str) -> Dict:
    """Return structured results in the Job Search JSON schema.

    Schema:
    {
      "profile": {
        "contacts": { "emails": [], "phones": [] },
        "skills": [],
        "experience": [],
        "education": [],
        "certifications": [],
        "preferred_roles": [],
        "preferred_industries": []
      },
      "jobs": [
        {
          "id": "",
          "title": "",
          "company": "",
          "location": "",
          "remote": true,
          "posted_at": "",
          "salary": "",
          "url": "",
          "source": "jsearch|serpapi"
        }
      ],
      "meta": {
        "sources_used": ["jsearch", "serpapi"],
        "count": 0,
        "location": null,
        "remote_only": false
      }
    }
    """
    try:
        profile_result: Dict = json.loads(profile_result_json) if profile_result_json else {}
    except Exception:
        profile_result = {}
    try:
        search_result: Dict = json.loads(search_result_json) if search_result_json else {}
    except Exception:
        search_result = {}

    profile = (profile_result or {}).get("profile", {})
    jobs = (search_result or {}).get("jobs", [])
    meta = (search_result or {}).get("meta", {})
    sources_used = (search_result or {}).get("sources_used", [])

    return {
        "profile": {
            "contacts": profile.get("contacts", {"emails": [], "phones": []}),
            "skills": profile.get("skills", []),
            "experience": profile.get("experience", []),
            "education": profile.get("education", []),
            "certifications": profile.get("certifications", []),
            "preferred_roles": profile.get("preferred_roles", []),
            "preferred_industries": profile.get("preferred_industries", []),
        },
        "jobs": [
            {
                "id": j.get("id"),
                "title": j.get("title"),
                "company": j.get("company"),
                "location": j.get("location"),
                "remote": j.get("remote"),
                "posted_at": j.get("posted_at"),
                "salary": j.get("salary"),
                "url": j.get("url"),
                "source": j.get("source"),
            }
            for j in jobs
        ],
        "meta": {
            "sources_used": sources_used,
            "count": meta.get("count", len(jobs)),
            "location": meta.get("location"),
            "remote_only": meta.get("remote_only", False),
        },
    }


