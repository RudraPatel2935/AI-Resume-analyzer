from __future__ import annotations

import json
from pathlib import Path

import joblib


MODEL_DIR = Path(__file__).resolve().parent
MODEL_PATH = MODEL_DIR / "feedback_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "feedback_vectorizer.pkl"
LABELS_PATH = MODEL_DIR / "feedback_labels.json"


SECTION_MESSAGES = {
    "summary_issue": "Rewrite the summary so it clearly names the target role, core stack, and one measurable outcome.",
    "skills_issue": "Add or reorder the Skills section so the most important tools and technologies appear near the top.",
    "projects_issue": "Strengthen projects with tools used, your role, and a concrete outcome or impact.",
    "experience_issue": "Expand experience bullets with action verbs, scope, and responsibilities that match the job.",
    "metrics_issue": "Quantify impact with numbers like percentages, counts, revenue, time saved, or users helped.",
    "keyword_alignment_issue": "Mirror the job description more naturally with role-specific keywords and domain language.",
}


def artifacts_available() -> bool:
    return MODEL_PATH.exists() and VECTORIZER_PATH.exists() and LABELS_PATH.exists()


def load_artifacts():
    if not artifacts_available():
        return None
    with LABELS_PATH.open("r", encoding="utf-8") as handle:
        metadata = json.load(handle)
    return {
        "model": joblib.load(MODEL_PATH),
        "vectorizer": joblib.load(VECTORIZER_PATH),
        "labels": metadata["labels"],
        "thresholds": metadata.get("thresholds", {}),
    }


def build_input_text(resume_text, job_description, category, ats_details=None):
    ats_details = ats_details or {}

    def _bucket(value):
        if value >= 65:
            return "high"
        if value >= 35:
            return "medium"
        return "low"

    return (
        f"CATEGORY_{category or 'unknown'} "
        f"ATS_{_bucket(float(ats_details.get('score', 0)))} "
        f"SKILL_COVERAGE_{_bucket(float(ats_details.get('skill_coverage', 0)))} "
        f"SEMANTIC_{_bucket(float(ats_details.get('semantic_similarity', 0)))} "
        f"KEYWORDS_{_bucket(float(ats_details.get('keyword_coverage', 0)))} "
        f"RESUME {resume_text or ''} JOB {job_description or ''}"
    )


def predict_issues(resume_text, job_description, category, ats_details=None):
    artifacts = load_artifacts()
    if not artifacts:
        return []

    input_text = build_input_text(resume_text, job_description, category, ats_details)
    vector = artifacts["vectorizer"].transform([input_text])
    probabilities = artifacts["model"].predict_proba(vector)

    detected = []
    for index, label in enumerate(artifacts["labels"]):
        threshold = artifacts["thresholds"].get(label, 0.5)
        probability = float(probabilities[index][0, 1])
        if probability >= threshold:
            detected.append((label, probability))

    detected.sort(key=lambda item: item[1], reverse=True)
    return detected


def issues_to_feedback(detected_issues, max_items=5):
    feedback = []
    for label, _probability in detected_issues[:max_items]:
        message = SECTION_MESSAGES.get(label)
        if message:
            feedback.append(message)
    return feedback