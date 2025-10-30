# Job Search Agent (Google ADK)

An advanced job search assistant that:
- Ingests a resume (PDF/DOCX/Text)
- Extracts a structured candidate profile
- Uses Playwright MCP tools to browse Naukri, LinkedIn, and Wellfound
- Returns consolidated results as JSON

## 1) Prerequisites
- Python 3.9+
- Node.js and npx installed (`node -v`, `npm -v`)
- Google ADK: `pip install google-adk`

Recommended virtualenv in repo root:
```
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install google-adk pdfminer.six python-docx requests
```

## 2) Model authentication (required)
Pick ONE:
- Google AI Studio (API key):
```
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY=YOUR_GOOGLE_AI_STUDIO_API_KEY
```
- Vertex AI (ADC):
```
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
export GOOGLE_CLOUD_LOCATION=YOUR_REGION
gcloud auth application-default login
```

## 3) Playwright MCP (browser) setup
The agent launches the Playwright MCP server via:
```
npx -y @playwright/mcp@latest
```
If npm errors, upgrade npm:
```
npm install -g npm
```
If you need the browser binaries:
```
./.venv/bin/python -m pip install playwright
./.venv/bin/python -m playwright install chromium
```

## 4) Run the Dev UI
From repo root:
```
./.venv/bin/adk web
```
Open the URL (e.g., http://127.0.0.1:8000) and select `job_search_agent`.

## 5) Usage
Provide a resume path and preferences in chat. Examples:
- "Use resume /absolute/path/to/resume.pdf. Location: Remote"
- "Use resume /absolute/path/to/resume.docx. Location: Bangalore"

The agent will:
1. `ingest_resume(file_path)`
2. `extract_profile(text)`
3. Browse job boards via Playwright MCP tools (Naukri, LinkedIn, Wellfound)
4. Fallback to internal aggregator if needed
5. `format_results(profile_result_json, search_result_json)` and return ONLY JSON

## 6) Optional APIs
Optional extra sources:
```
export RAPIDAPI_JSEARCH_KEY=YOUR_KEY
export SERPAPI_KEY=YOUR_KEY
```

## 7) Troubleshooting
- Model auth errors: set `GOOGLE_API_KEY` or Vertex AI envs.
- npm 404 on Playwright MCP: `npm install -g npm`; ensure `npx` is in PATH.
- Headless browsing blocked/CAPTCHA: retry; we can refine selectors/waits per site.

## 8) Tools
- `ingest_resume(file_path)`
- `extract_profile(text)`
- `search_jobs(profile_json, location, remote)` (fallback aggregator)
- `format_results(profile_result_json, search_result_json)`

JSON output (simplified):
```
{
  "profile": { "contacts": {"emails": [], "phones": []}, "skills": [], "experience": [], "education": [], "certifications": [], "preferred_roles": [], "preferred_industries": [] },
  "jobs": [{ "id": "", "title": "", "company": "", "location": "", "remote": true, "posted_at": "", "salary": "", "url": "", "source": "" }],
  "meta": { "sources_used": [], "count": 0, "location": null, "remote_only": false }
}
```
