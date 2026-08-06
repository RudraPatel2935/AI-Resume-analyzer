import re

from ml_models.feedback_recommendation.predict import issues_to_feedback, predict_issues
from ml_models.skill_recommendation.skill_model import recommend_skills


SECTION_PATTERNS = {
    "skills": re.compile(r"\b(skills?|technical skills|core competencies)\b", re.IGNORECASE),
    "experience": re.compile(r"\b(experience|work experience|professional experience)\b", re.IGNORECASE),
    "projects": re.compile(r"\b(projects?|selected projects)\b", re.IGNORECASE),
    "education": re.compile(r"\b(education|academic background)\b", re.IGNORECASE),
    "achievements": re.compile(r"\b(achievements?|accomplishments|awards?)\b", re.IGNORECASE),
    "summary": re.compile(r"\b(summary|profile|objective)\b", re.IGNORECASE),
    "certifications": re.compile(r"\b(certifications?|licenses?)\b", re.IGNORECASE),
}


def _detect_sections(resume_text):
    text = resume_text or ""
    return {section: bool(pattern.search(text)) for section, pattern in SECTION_PATTERNS.items()}


def _has_quantified_results(resume_text):
    text = resume_text or ""
    return bool(re.search(r"\b\d+(?:\.\d+)?\s*(?:%|k|m|million|thousand|x|years?|months?|users?|clients?|projects?)\b", text, re.IGNORECASE))


def _top_missing_skills(missing_skills, limit=3):
    if not missing_skills:
        return []
    return list(dict.fromkeys(missing_skills))[:limit]


def generate_feedback(
    missing_skills,
    category,
    resume_text=None,
    job_description=None,
    ats_details=None,
    as_questions=False,
):
    recommendations = recommend_skills(missing_skills, category)
    sections = _detect_sections(resume_text)
    feedback_points = []

    model_issues = predict_issues(resume_text, job_description, category, ats_details)
    model_feedback = issues_to_feedback(model_issues)

    if model_feedback:
        feedback_points.extend(model_feedback)

    score = (ats_details or {}).get("score", 0)
    skill_coverage = (ats_details or {}).get("skill_coverage", 0)
    semantic_similarity = (ats_details or {}).get("semantic_similarity", 0)
    keyword_coverage = (ats_details or {}).get("keyword_coverage", 0)

    if not feedback_points and score >= 80:
        feedback_points.append("Strong match overall. Focus on making achievements more measurable and role-specific.")
    elif not feedback_points and score >= 65:
        feedback_points.append("Good match overall. Improve keyword alignment and make your impact easier to see at a glance.")
    elif not feedback_points:
        feedback_points.append("The resume needs stronger alignment to the job description, especially in skills and project evidence.")

    missing_skills_list = _top_missing_skills(missing_skills)
    if missing_skills_list:
        feedback_points.append(
            "Add or emphasize these missing skills where they are genuinely relevant: "
            + ", ".join(missing_skills_list)
            + "."
        )

    if not sections["skills"]:
        feedback_points.append("Add a dedicated Skills section so the ATS can find your tools and technologies quickly.")

    if not sections["projects"] and category.lower() in {"it", "software engineering", "computer science", "data science"}:
        feedback_points.append("Include 1-3 project bullets with the tools used, your role, and the outcome.")

    if not sections["experience"]:
        feedback_points.append("Add a clear Experience section or strengthen internship/work bullets with action verbs.")

    if not sections["achievements"] and not _has_quantified_results(resume_text):
        feedback_points.append("Quantify results with numbers such as percentages, counts, time saved, or revenue impact.")

    if keyword_coverage < 35:
        feedback_points.append("Mirror more job-description keywords naturally in your summary, skills, and project bullets.")

    if skill_coverage < 50:
        feedback_points.append("Raise skill coverage by adding the most important required tools only if you actually know them.")

    if semantic_similarity < 25:
        feedback_points.append("Rewrite the summary and project descriptions to better reflect the job target and domain language.")

    if not feedback_points:
        feedback_points = recommendations or [
            "Your profile is a reasonable match. Strengthen project depth and quantify results.",
        ]

    if as_questions:
        return [f"What evidence shows improvement in this area: {point}" for point in feedback_points[:5]]

    if recommendations and len(feedback_points) < 2:
        feedback_points.extend(recommendations[:3])

    return "\n".join(f"- {point}" for point in feedback_points[:6])