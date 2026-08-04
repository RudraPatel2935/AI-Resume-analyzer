from ml_models.skill_recommendation.skill_model import recommend_skills


def generate_feedback(missing_skills, category, as_questions=False):
    recommendations = recommend_skills(missing_skills, category)

    if as_questions:
        return [f"How have you practiced {item}?" for item in recommendations[:5]]

    if not recommendations:
        return "Your profile is a reasonable match. Strengthen project depth and quantify results."

    return " ".join(recommendations)