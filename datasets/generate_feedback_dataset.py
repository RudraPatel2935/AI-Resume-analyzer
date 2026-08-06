from __future__ import annotations

import csv
import random
from pathlib import Path


random.seed(42)


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "feedback_dataset.csv"


DOMAIN_PROFILES = {
    "Software Engineering": {
        "skills": ["Python", "Java", "JavaScript", "React", "Flask", "Django", "REST APIs", "Git", "Docker", "SQL"],
        "projects": ["full-stack dashboard", "API service", "microservices platform", "developer portal"],
        "experience": ["backend developer", "software engineer intern", "full-stack engineer", "application developer"],
        "metrics": ["24%", "18%", "3x", "40%", "12"],
    },
    "Data Science": {
        "skills": ["Python", "Pandas", "NumPy", "scikit-learn", "SQL", "statistics", "feature engineering", "data visualization"],
        "projects": ["forecasting pipeline", "analytics dashboard", "classification model", "data wrangling workflow"],
        "experience": ["data analyst intern", "machine learning intern", "analytics associate", "data science intern"],
        "metrics": ["15%", "22%", "1,200", "8%", "30%"],
    },
    "AI/ML": {
        "skills": ["Python", "TensorFlow", "PyTorch", "machine learning", "deep learning", "NLP", "computer vision", "model tuning"],
        "projects": ["recommendation engine", "LLM assistant", "vision classifier", "training pipeline"],
        "experience": ["ML engineer intern", "research intern", "AI developer", "data scientist"],
        "metrics": ["91%", "14%", "2x", "36%", "5,000"],
    },
    "Mechanical Engineering": {
        "skills": ["AutoCAD", "SolidWorks", "CAD", "MATLAB", "FMEA", "GD&T", "manufacturing", "mechanical design"],
        "projects": ["machine component design", "thermal analysis project", "prototype assembly", "manufacturing line improvement"],
        "experience": ["design engineer intern", "mechanical engineer", "production engineer", "CAD intern"],
        "metrics": ["17%", "11%", "4", "28%", "6"],
    },
    "Civil Engineering": {
        "skills": ["AutoCAD", "Revit", "STAAD Pro", "construction management", "structural analysis", "surveying", "RCC design", "site execution"],
        "projects": ["bridge design", "building project", "site supervision", "structural estimation"],
        "experience": ["site engineer intern", "civil engineer", "planning engineer", "estimation engineer"],
        "metrics": ["9%", "16%", "3", "21%", "10"],
    },
    "Biomedical": {
        "skills": ["MATLAB", "medical imaging", "bioinformatics", "clinical research", "biostatistics", "PCR", "signal processing"],
        "projects": ["diagnostic workflow", "imaging analysis system", "clinical study", "device validation"],
        "experience": ["research assistant", "biomedical intern", "clinical research intern", "lab assistant"],
        "metrics": ["13%", "7", "2x", "19%", "450"],
    },
    "Finance": {
        "skills": ["Excel", "accounting", "financial modeling", "risk analysis", "valuation", "forecasting", "taxation", "budgeting"],
        "projects": ["investment analysis", "budget dashboard", "audit process", "portfolio model"],
        "experience": ["finance intern", "analyst", "accounts associate", "risk analyst"],
        "metrics": ["25%", "$50K", "4%", "18", "2x"],
    },
    "Marketing": {
        "skills": ["SEO", "content strategy", "Google Analytics", "CRM", "brand management", "social media", "campaign planning"],
        "projects": ["digital campaign", "content calendar", "brand launch", "growth strategy"],
        "experience": ["marketing intern", "content strategist", "growth associate", "brand coordinator"],
        "metrics": ["32%", "1.4x", "3,200", "11%", "9"],
    },
}


SCENARIOS = [
    {
        "name": "strong",
        "weights": {"summary_issue": 0.12, "skills_issue": 0.12, "projects_issue": 0.12, "experience_issue": 0.12, "metrics_issue": 0.12, "keyword_alignment_issue": 0.12},
        "summary": "Results-driven {category} professional with hands-on project experience and measurable outcomes.",
    },
    {
        "name": "missing_skills",
        "weights": {"summary_issue": 0.18, "skills_issue": 0.90, "projects_issue": 0.20, "experience_issue": 0.15, "metrics_issue": 0.15, "keyword_alignment_issue": 0.25},
        "summary": "Motivated {category} candidate with practical project exposure and a willingness to learn.",
    },
    {
        "name": "weak_projects",
        "weights": {"summary_issue": 0.15, "skills_issue": 0.20, "projects_issue": 0.92, "experience_issue": 0.15, "metrics_issue": 0.20, "keyword_alignment_issue": 0.20},
        "summary": "Professional with technical knowledge and coursework foundation in {category}.",
    },
    {
        "name": "weak_experience",
        "weights": {"summary_issue": 0.18, "skills_issue": 0.18, "projects_issue": 0.18, "experience_issue": 0.90, "metrics_issue": 0.18, "keyword_alignment_issue": 0.24},
        "summary": "Entry-level {category} profile with academic projects and internship exposure.",
    },
    {
        "name": "weak_metrics",
        "weights": {"summary_issue": 0.20, "skills_issue": 0.18, "projects_issue": 0.18, "experience_issue": 0.18, "metrics_issue": 0.92, "keyword_alignment_issue": 0.20},
        "summary": "Detail-oriented {category} candidate with solid execution and project involvement.",
    },
    {
        "name": "keyword_mismatch",
        "weights": {"summary_issue": 0.22, "skills_issue": 0.22, "projects_issue": 0.20, "experience_issue": 0.20, "metrics_issue": 0.18, "keyword_alignment_issue": 0.92},
        "summary": "Ambitious professional building experience across related technical and business tasks.",
    },
    {
        "name": "mixed_gaps",
        "weights": {"summary_issue": 0.45, "skills_issue": 0.55, "projects_issue": 0.55, "experience_issue": 0.45, "metrics_issue": 0.50, "keyword_alignment_issue": 0.45},
        "summary": "Adaptable {category} candidate with exposure to technical projects and collaborative work.",
    },
]


def _sample_skills(category_config, issue_name):
    skills = list(category_config["skills"])
    if issue_name == "missing_skills":
        return random.sample(skills[: max(3, len(skills) // 2)], k=3)
    if issue_name == "keyword_mismatch":
        return random.sample(skills, k=2) + ["communication", "teamwork"]
    if issue_name == "mixed_gaps":
        return random.sample(skills, k=3)
    return random.sample(skills, k=min(5, len(skills)))


def _sample_metrics(category_config, issue_name):
    metrics = category_config["metrics"]
    if issue_name == "weak_metrics":
        return []
    if issue_name == "keyword_mismatch":
        return [random.choice(metrics)]
    return random.sample(metrics, k=min(2, len(metrics)))


def _build_resume_text(category, issue_name, category_config):
    skills = _sample_skills(category_config, issue_name)
    metrics = _sample_metrics(category_config, issue_name)
    project = random.choice(category_config["projects"])
    experience = random.choice(category_config["experience"])

    summary = next(item["summary"].format(category=category) for item in SCENARIOS if item["name"] == issue_name)
    skills_section = "Skills: " + ", ".join(skills) if issue_name != "missing_skills" else "Skills: Python, Excel, communication"

    if issue_name == "weak_projects":
        projects_section = "Projects: Academic coursework and group assignments."
    elif issue_name == "keyword_mismatch":
        projects_section = "Projects: Built a general solution focused on collaboration, documentation, and process improvement."
    else:
        metric_phrase = f" Achieved {random.choice(metrics)} improvement." if metrics else ""
        projects_section = f"Projects: Built a {project} using {', '.join(skills[:4])}.{metric_phrase}"

    if issue_name == "weak_experience":
        experience_section = "Experience: Assisted with tasks and supported team projects."
    else:
        metric_phrase = f" Delivered {random.choice(metrics)} improvement." if metrics else ""
        experience_section = f"Experience: Worked as a {experience} and contributed to delivery, testing, and stakeholder communication.{metric_phrase}"

    achievements_section = (
        "Achievements: Improved delivery by 20% and handled 3 client-facing projects."
        if issue_name not in {"weak_metrics", "mixed_gaps"}
        else "Achievements: Contributed to team outcomes and supported process improvement."
    )

    if issue_name == "keyword_mismatch":
        summary = "Motivated professional with exposure to teamwork, reporting, and documentation in a fast-paced environment."

    if issue_name == "mixed_gaps":
        skills_section = "Skills: Python, SQL, Excel"
        projects_section = "Projects: Group project on reporting and process improvement."
        experience_section = "Experience: Supported operations and collaborated on tasks."
        achievements_section = "Achievements: Helped the team complete deliverables."

    return "\n".join([summary, skills_section, projects_section, experience_section, achievements_section])


def _build_job_description(category, category_config):
    skills = random.sample(category_config["skills"], k=min(5, len(category_config["skills"])))
    project = random.choice(category_config["projects"])
    experience = random.choice(category_config["experience"])
    return (
        f"We are hiring a {category} professional with experience in {', '.join(skills[:4])}. "
        f"Candidates should have hands-on work in {project}, strong communication, and a background as a {experience}. "
        f"Preference for measurable results, ownership, and domain-specific keywords."
    )


def _bucket(value):
    if value >= 0.75:
        return "high"
    if value >= 0.45:
        return "medium"
    return "low"


def _score_from_labels(issue_flags):
    penalties = {
        "summary_issue": 10,
        "skills_issue": 18,
        "projects_issue": 16,
        "experience_issue": 14,
        "metrics_issue": 12,
        "keyword_alignment_issue": 15,
    }
    score = 92
    for label, present in issue_flags.items():
        if present:
            score -= penalties[label]
    return max(22, min(score, 96))


def main() -> None:
    rows = []
    categories = list(DOMAIN_PROFILES.keys())
    rows_per_category = 2000

    for category in categories:
        category_config = DOMAIN_PROFILES[category]
        for _ in range(rows_per_category):
            scenario = random.choice(SCENARIOS)
            issue_flags = {
                label: random.random() < probability for label, probability in scenario["weights"].items()
            }

            resume_text = _build_resume_text(category, scenario["name"], category_config)
            job_description = _build_job_description(category, category_config)

            skill_count = len(category_config["skills"])
            matched_skill_count = max(1, int(skill_count * (0.85 if scenario["name"] == "strong" else random.uniform(0.25, 0.75))))
            skill_coverage = matched_skill_count / skill_count
            semantic_similarity = 0.74 if scenario["name"] == "strong" else random.uniform(0.18, 0.68)
            keyword_coverage = 0.7 if scenario["name"] == "strong" else random.uniform(0.12, 0.62)
            ats_score = _score_from_labels(issue_flags)

            rows.append(
                {
                    "category": category,
                    "resume_text": resume_text,
                    "job_description": job_description,
                    "ats_score": ats_score,
                    "skill_coverage": round(skill_coverage * 100, 2),
                    "semantic_similarity": round(semantic_similarity * 100, 2),
                    "keyword_coverage": round(keyword_coverage * 100, 2),
                    "summary_issue": int(issue_flags["summary_issue"]),
                    "skills_issue": int(issue_flags["skills_issue"]),
                    "projects_issue": int(issue_flags["projects_issue"]),
                    "experience_issue": int(issue_flags["experience_issue"]),
                    "metrics_issue": int(issue_flags["metrics_issue"]),
                    "keyword_alignment_issue": int(issue_flags["keyword_alignment_issue"]),
                }
            )

    random.shuffle(rows)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "category",
                "resume_text",
                "job_description",
                "ats_score",
                "skill_coverage",
                "semantic_similarity",
                "keyword_coverage",
                "summary_issue",
                "skills_issue",
                "projects_issue",
                "experience_issue",
                "metrics_issue",
                "keyword_alignment_issue",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} feedback rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()