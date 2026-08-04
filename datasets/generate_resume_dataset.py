from __future__ import annotations

import csv
import random
from pathlib import Path


random.seed(42)


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "resume_dataset.csv"


CATALOG = {
    "Software Engineering": {
        "skills": ["Python", "Java", "JavaScript", "React", "Flask", "Django", "REST APIs", "Git", "Docker", "SQL"],
        "projects": ["web application", "microservices platform", "backend service", "full-stack portal", "API layer"],
        "extras": ["agile delivery", "code review", "unit testing", "CI/CD", "cloud deployment"],
    },
    "Data Science": {
        "skills": ["Python", "Pandas", "NumPy", "scikit-learn", "statistics", "data visualization", "SQL", "model evaluation"],
        "projects": ["prediction pipeline", "analytics dashboard", "forecasting system", "data cleaning workflow", "classification model"],
        "extras": ["feature engineering", "exploratory analysis", "A/B testing", "dashboard reporting", "data wrangling"],
    },
    "AI/ML": {
        "skills": ["Python", "TensorFlow", "PyTorch", "machine learning", "deep learning", "NLP", "computer vision", "model tuning"],
        "projects": ["neural network", "classification model", "recommendation engine", "LLM assistant", "vision system"],
        "extras": ["hyperparameter optimization", "data preprocessing", "MLOps", "training pipeline", "feature selection"],
    },
    "Mechanical Engineering": {
        "skills": ["AutoCAD", "SolidWorks", "CAD", "mechanical design", "MATLAB", "manufacturing", "FMEA", "GD&T"],
        "projects": ["product design", "machine component", "prototype assembly", "thermal system", "manufacturing line"],
        "extras": ["finite element analysis", "tolerance stack-up", "process optimization", "quality inspection", "technical drawing"],
    },
    "Civil Engineering": {
        "skills": ["AutoCAD", "Revit", "STAAD Pro", "construction management", "structural analysis", "surveying", "RCC design", "site execution"],
        "projects": ["bridge design", "building project", "site supervision", "infrastructure planning", "structural estimation"],
        "extras": ["BOQ preparation", "quality control", "project scheduling", "vendor coordination", "safety compliance"],
    },
    "Biomedical": {
        "skills": ["MATLAB", "medical imaging", "bioinformatics", "clinical research", "biostatistics", "signal processing", "healthcare analytics", "PCR"],
        "projects": ["diagnostic system", "imaging workflow", "clinical study", "patient data analysis", "device validation"],
        "extras": ["regulatory documentation", "lab protocol", "research methodology", "data interpretation", "equipment testing"],
    },
    "Finance": {
        "skills": ["Excel", "accounting", "financial modeling", "risk analysis", "valuation", "forecasting", "taxation", "budgeting"],
        "projects": ["investment analysis", "budget dashboard", "audit process", "financial report", "portfolio model"],
        "extras": ["variance analysis", "cash flow planning", "compliance review", "cost optimization", "KPI tracking"],
    },
    "Marketing": {
        "skills": ["SEO", "content strategy", "Google Analytics", "CRM", "brand management", "social media", "campaign planning", "lead generation"],
        "projects": ["digital campaign", "content calendar", "brand launch", "customer funnel", "growth strategy"],
        "extras": ["market research", "A/B testing", "conversion optimization", "audience segmentation", "performance reporting"],
    },
}


TEMPLATES = [
    "{skills} focused on {project} with experience in {extras}.",
    "Worked on {project} using {skills} and delivered results through {extras}.",
    "Professional background includes {skills}, {project}, and strong emphasis on {extras}.",
    "Hands-on experience with {skills} in {project}, including {extras}.",
    "Built and improved {project} by applying {skills} and {extras}.",
]


EXTRA_PHRASES = [
    "cross-functional collaboration",
    "stakeholder communication",
    "documentation",
    "problem solving",
    "process improvement",
    "business analysis",
    "technical writing",
    "presentation skills",
]


def build_sentence(category: str) -> str:
    config = CATALOG[category]
    skill_sample = random.sample(config["skills"], k=min(4, len(config["skills"])))
    project = random.choice(config["projects"])
    extras_pool = list(config["extras"]) + random.sample(EXTRA_PHRASES, k=2)
    extras = ", ".join(random.sample(extras_pool, k=min(3, len(extras_pool))))
    template = random.choice(TEMPLATES)
    sentence = template.format(
        skills=", ".join(skill_sample),
        project=project,
        extras=extras,
    )
    addons = random.sample(config["skills"], k=min(2, len(config["skills"])))
    return f"{sentence} Additional keywords: {' '.join(addons)}."


def main() -> None:
    categories = list(CATALOG.keys())
    rows = []
    rows_per_category = 625

    for category in categories:
        for _ in range(rows_per_category):
            rows.append({"resume_text": build_sentence(category), "category": category})

    random.shuffle(rows)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["resume_text", "category"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()