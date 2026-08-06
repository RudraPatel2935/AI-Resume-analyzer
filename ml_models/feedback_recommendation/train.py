from __future__ import annotations

import json
from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from nlp.text_cleaner import clean_text


DATASET_PATH = PROJECT_ROOT / "datasets" / "feedback_dataset.csv"
OUTPUT_DIR = Path(__file__).resolve().parent
LABEL_COLUMNS = [
    "summary_issue",
    "skills_issue",
    "projects_issue",
    "experience_issue",
    "metrics_issue",
    "keyword_alignment_issue",
]


def _bucketize(value, boundaries=(35, 65)):
    if value < boundaries[0]:
        return "low"
    if value < boundaries[1]:
        return "medium"
    return "high"


def load_dataset():
    data = pd.read_csv(DATASET_PATH)
    for column in ["resume_text", "job_description", "category"]:
        data[column] = data[column].fillna("").astype(str)
    data["combined_text"] = data.apply(
        lambda row: (
            f"CATEGORY_{row['category']} "
            f"ATS_{_bucketize(float(row['ats_score']))} "
            f"SKILL_COVERAGE_{_bucketize(float(row['skill_coverage']))} "
            f"SEMANTIC_{_bucketize(float(row['semantic_similarity']))} "
            f"KEYWORDS_{_bucketize(float(row['keyword_coverage']))} "
            f"RESUME {clean_text(row['resume_text'])} JOB {clean_text(row['job_description'])}"
        ),
        axis=1,
    )
    return data


def evaluate_thresholds(y_true, probas):
    thresholds = {}
    for index, label in enumerate(LABEL_COLUMNS):
        best_threshold = 0.5
        best_score = -1.0
        for threshold in [0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65]:
            preds = (probas[index][:, 1] >= threshold).astype(int)
            score = f1_score(y_true[label], preds, zero_division=0)
            if score > best_score:
                best_score = score
                best_threshold = threshold
        thresholds[label] = best_threshold
    return thresholds


def train():
    data = load_dataset()
    x_train, x_test, y_train, y_test = train_test_split(
        data["combined_text"],
        data[LABEL_COLUMNS],
        test_size=0.2,
        random_state=42,
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000)
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    model = MultiOutputClassifier(
        LogisticRegression(max_iter=2500, class_weight="balanced", solver="liblinear")
    )
    model.fit(x_train_vec, y_train)

    raw_predictions = model.predict(x_test_vec)
    print("Overall micro F1:", round(f1_score(y_test, raw_predictions, average="micro", zero_division=0), 4))

    y_test_df = pd.DataFrame(y_test, columns=LABEL_COLUMNS)
    probas = model.predict_proba(x_test_vec)
    thresholds = evaluate_thresholds(y_test_df, probas)

    for index, label in enumerate(LABEL_COLUMNS):
        label_predictions = (probas[index][:, 1] >= thresholds[label]).astype(int)
        print(f"\nLabel: {label}")
        print(classification_report(y_test_df[label], label_predictions, zero_division=0))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUTPUT_DIR / "feedback_model.pkl")
    joblib.dump(vectorizer, OUTPUT_DIR / "feedback_vectorizer.pkl")
    with (OUTPUT_DIR / "feedback_labels.json").open("w", encoding="utf-8") as handle:
        json.dump({"labels": LABEL_COLUMNS, "thresholds": thresholds}, handle, indent=2)

    print("Saved feedback model artifacts to", OUTPUT_DIR)


if __name__ == "__main__":
    train()