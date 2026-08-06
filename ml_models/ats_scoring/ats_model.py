from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp.skill_extractor import extract_skills, load_skills_database
from nlp.text_cleaner import clean_text


def _safe_ratio(numerator, denominator, fallback=0.0):
    if denominator <= 0:
        return fallback
    return numerator / denominator


def _token_set(text):
    return {
        token
        for token in (text or "").split()
        if len(token) > 2 and token not in ENGLISH_STOP_WORDS and not token.isdigit()
    }


def _section_signal(text):
    section_keywords = {
        "experience",
        "education",
        "skills",
        "projects",
        "certifications",
        "summary",
        "achievements",
    }
    tokens = set((text or "").split())
    covered = len(section_keywords.intersection(tokens))
    return _safe_ratio(covered, len(section_keywords), fallback=0.0)


def _extract_required_terms(cleaned_job_text):
    generic_terms = {
        "experience",
        "knowledge",
        "ability",
        "strong",
        "excellent",
        "team",
        "work",
        "candidate",
        "role",
        "responsibilities",
        "requirements",
        "years",
    }

    tokens = [t for t in (cleaned_job_text or "").split() if len(t) >= 3 and t not in ENGLISH_STOP_WORDS]
    unigrams = [t for t in tokens if t not in generic_terms]

    bigrams = []
    for idx in range(len(tokens) - 1):
        left = tokens[idx]
        right = tokens[idx + 1]
        if left in generic_terms or right in generic_terms:
            continue
        phrase = f"{left} {right}"
        if len(phrase) >= 7:
            bigrams.append(phrase)

    selected_unigrams = list(dict.fromkeys(unigrams))[:25]
    selected_bigrams = list(dict.fromkeys(bigrams))[:20]
    required_terms = list(dict.fromkeys(selected_bigrams + selected_unigrams))
    return required_terms[:35]


def _term_coverage(resume_text, required_terms):
    if not required_terms:
        return 0.0

    resume = f" {(resume_text or '').lower()} "
    hits = 0
    for term in required_terms:
        t = term.lower()
        if f" {t} " in resume:
            hits += 1
    return _safe_ratio(hits, len(required_terms), fallback=0.0)


def analyze_ats(resume_text, job_description):
    raw_resume = resume_text or ""
    raw_job = job_description or ""

    cleaned_resume = clean_text(raw_resume)
    cleaned_job = clean_text(raw_job)

    word_vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    word_tfidf = word_vectorizer.fit_transform([cleaned_resume, cleaned_job])
    word_similarity = float(cosine_similarity(word_tfidf[0:1], word_tfidf[1:2])[0][0])

    char_vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    char_tfidf = char_vectorizer.fit_transform([cleaned_resume, cleaned_job])
    char_similarity = float(cosine_similarity(char_tfidf[0:1], char_tfidf[1:2])[0][0])
    semantic_similarity = (0.65 * word_similarity) + (0.35 * char_similarity)

    skills_db = load_skills_database("datasets/skills.json")
    resume_skills = set(extract_skills(raw_resume, skills_db))
    job_skills = set(extract_skills(raw_job, skills_db))

    matched_skills = sorted(resume_skills.intersection(job_skills))
    missing_skills = sorted(job_skills.difference(resume_skills))

    skill_coverage = _safe_ratio(len(matched_skills), len(job_skills), fallback=0.55)

    resume_tokens = _token_set(cleaned_resume)
    job_tokens = _token_set(cleaned_job)
    keyword_coverage = _safe_ratio(
        len(resume_tokens.intersection(job_tokens)),
        len(job_tokens),
        fallback=0.0,
    )

    required_terms = _extract_required_terms(cleaned_job)
    requirement_coverage = _term_coverage(raw_resume, required_terms)

    section_signal = _section_signal(cleaned_resume)

    raw_score = (
        (0.38 * skill_coverage)
        + (0.30 * semantic_similarity)
        + (0.17 * keyword_coverage)
        + (0.10 * requirement_coverage)
        + (0.05 * section_signal)
    )
    score = raw_score * 100

    # Calibrate likely good matches so wording differences do not produce overly low ATS scores.
    if skill_coverage >= 0.60 and semantic_similarity >= 0.25 and score < 65:
        score = max(score, 65 + ((skill_coverage - 0.60) * 20) + ((semantic_similarity - 0.25) * 20))
    if skill_coverage >= 0.80 and semantic_similarity >= 0.35 and score < 75:
        score = 75
    if requirement_coverage >= 0.50 and semantic_similarity >= 0.30 and score < 70:
        score = 70
    if requirement_coverage >= 0.65 and skill_coverage >= 0.55 and score < 74:
        score = 74

    score = round(min(score, 98.0), 2)

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_coverage": round(skill_coverage * 100, 2),
        "semantic_similarity": round(semantic_similarity * 100, 2),
        "keyword_coverage": round(keyword_coverage * 100, 2),
        "requirement_coverage": round(requirement_coverage * 100, 2),
        "required_terms": required_terms,
    }