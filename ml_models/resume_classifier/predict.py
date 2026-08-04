from pathlib import Path
import sys

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from nlp.text_cleaner import clean_text


MODEL_DIR = Path(__file__).resolve().parent


def _artifacts_exist():
    return (MODEL_DIR / "model.pkl").exists() and (MODEL_DIR / "vectorizer.pkl").exists()


def _load_artifacts():
    if not _artifacts_exist():
        raise FileNotFoundError(
            "Resume classifier artifacts are missing. Run ml_models/resume_classifier/train.py to create model.pkl and vectorizer.pkl."
        )
    model = joblib.load(MODEL_DIR / "model.pkl")
    vectorizer = joblib.load(MODEL_DIR / "vectorizer.pkl")
    return model, vectorizer


def predict_category(resume_text):
    model, vectorizer = _load_artifacts()
    cleaned_text = clean_text(resume_text)
    vector = vectorizer.transform([cleaned_text])
    return model.predict(vector)[0]