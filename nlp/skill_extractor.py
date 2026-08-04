import json
import os


def load_skills_database(skills_file):
    if os.path.exists(skills_file):
        with open(skills_file, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {}


def extract_skills(text, skills_db):
    text_lower = (text or "").lower()
    found_skills = []
    for domain, skills in skills_db.items():
        for skill in skills:
            if skill.lower() in text_lower and skill not in found_skills:
                found_skills.append(skill)
    return found_skills