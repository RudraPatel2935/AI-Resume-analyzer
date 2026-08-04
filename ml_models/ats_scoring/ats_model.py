from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp.skill_extractor import extract_skills, load_skills_database
from nlp.text_cleaner import clean_text


def analyze_ats(resume_text, job_description):
    cleaned_resume = clean_text(resume_text)
    cleaned_job = clean_text(job_description)

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_job])
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    score = round(similarity * 100, 2)

    skills_db = load_skills_database("datasets/skills.json")
    resume_skills = set(extract_skills(cleaned_resume, skills_db))
    job_skills = set(extract_skills(cleaned_job, skills_db))

    matched_skills = sorted(resume_skills.intersection(job_skills))
    missing_skills = sorted(job_skills.difference(resume_skills))

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }