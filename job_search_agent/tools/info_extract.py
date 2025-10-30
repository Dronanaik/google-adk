from typing import Dict, List
import re


def _extract_emails(text: str) -> List[str]:
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    return re.findall(pattern, text)


def _extract_phones(text: str) -> List[str]:
    pattern = r"(?:\+\d{1,3}[\s-]?)?(?:\(\d{2,4}\)[\s-]?|\d{2,4}[\s-])?\d{3,4}[\s-]?\d{3,4}"
    return [p.strip() for p in re.findall(pattern, text)]


def extract_profile(text: str) -> Dict:
    """Extract core profile fields from resume text using lightweight heuristics.

    This function is intentionally dependency-light. For production-grade extraction,
    replace heuristics with an NLP pipeline or a model-based extractor.

    Args:
        text: Plain text content of the resume.

    Returns:
        dict: { status, profile: { skills, experience, education, certifications, preferred_roles, preferred_industries, contacts } }
    """
    if not text or not text.strip():
        return {"status": "error", "error_message": "Empty resume text"}

    lower = text.lower()

    possible_skill_headers = ("skills", "technical skills", "key skills")
    possible_exp_headers = ("experience", "work experience", "employment", "professional experience")
    possible_edu_headers = ("education", "academic background")
    possible_cert_headers = ("certifications", "licenses")
    possible_roles_headers = ("roles", "target roles", "preferred roles")
    possible_industry_headers = ("industries", "preferred industries")

    def section(header_keywords: tuple[str, ...]) -> str:
        for hk in header_keywords:
            idx = lower.find(hk)
            if idx != -1:
                end = len(text)
                # naive split: next uppercase header or double newline
                nxt = re.search(r"\n\s*\n|\n[A-Z][A-Za-z\s]{2,}:?\n", text[idx + len(hk) :])
                if nxt:
                    end = idx + len(hk) + nxt.start()
                return text[idx:end]
        return ""

    skills_sec = section(possible_skill_headers)
    experience_sec = section(possible_exp_headers)
    education_sec = section(possible_edu_headers)
    certs_sec = section(possible_cert_headers)
    roles_sec = section(possible_roles_headers)
    industries_sec = section(possible_industry_headers)

    def bullets(sec: str) -> List[str]:
        lines = [l.strip(" -*•\t") for l in sec.splitlines()]
        return [l for l in lines if l and len(l) < 200]

    profile = {
        "contacts": {
            "emails": _extract_emails(text),
            "phones": _extract_phones(text),
        },
        "skills": bullets(skills_sec),
        "experience": bullets(experience_sec),
        "education": bullets(education_sec),
        "certifications": bullets(certs_sec),
        "preferred_roles": bullets(roles_sec),
        "preferred_industries": bullets(industries_sec),
        "raw_excerpt": text[:4000],
    }

    return {"status": "success", "profile": profile}


