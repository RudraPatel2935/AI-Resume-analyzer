from collections import defaultdict


DOMAIN_SKILL_HINTS = defaultdict(
    list,
    {
        "it": ["Python", "Java", "React", "SQL", "Docker", "AWS", "Machine Learning"],
        "mechanical": ["AutoCAD", "SolidWorks", "MATLAB"],
        "biomedical": ["Bioinformatics", "Medical Imaging", "Clinical Research"],
        "finance": ["Excel", "Accounting", "Financial Modeling"],
        "marketing": ["SEO", "Content Strategy", "Google Analytics", "CRM"],
        "civil": ["AutoCAD", "STAAD Pro", "Revit", "Construction Management"],
    },
)


def recommend_skills(missing_skills, category):
    recommendations = []
    category_key = (category or "").lower()
    if missing_skills:
        recommendations.extend([f"Learn {skill}." for skill in missing_skills])
    for hint in DOMAIN_SKILL_HINTS.get(category_key, []):
        if hint not in recommendations:
            recommendations.append(f"Strengthen {hint}.")
    return recommendations[:8]