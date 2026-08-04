from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from nlp.text_cleaner import clean_text


BASE_DIR = PROJECT_ROOT
DATASET_PATH = BASE_DIR / "datasets" / "resume_dataset.csv"
OUTPUT_DIR = Path(__file__).resolve().parent


def load_dataset():
    data = pd.read_csv(DATASET_PATH)
    data["resume_text"] = data["resume_text"].fillna("").apply(clean_text)
    return data


def evaluate_model(model, x_test, y_test):
    predictions = model.predict(x_test)
    return {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, average="weighted", zero_division=0),
        "recall": recall_score(y_test, predictions, average="weighted", zero_division=0),
        "f1": f1_score(y_test, predictions, average="weighted", zero_division=0),
    }


def train():
    data = load_dataset()
    x_train, x_test, y_train, y_test = train_test_split(
        data["resume_text"], data["category"], test_size=0.2, random_state=42, stratify=data["category"]
    )

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=2000),
        "naive_bayes": MultinomialNB(),
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=42),
    }

    best_name = None
    best_model = None
    best_metrics = None
    best_score = -1.0

    for name, model in candidates.items():
        model.fit(x_train_vec, y_train)
        metrics = evaluate_model(model, x_test_vec, y_test)
        print(f"{name} -> accuracy={metrics['accuracy']:.4f}, precision={metrics['precision']:.4f}, recall={metrics['recall']:.4f}, f1={metrics['f1']:.4f}")
        if metrics["accuracy"] > best_score:
            best_score = metrics["accuracy"]
            best_name = name
            best_model = model
            best_metrics = metrics

    joblib.dump(best_model, OUTPUT_DIR / "model.pkl")
    joblib.dump(vectorizer, OUTPUT_DIR / "vectorizer.pkl")

    print(f"Best model: {best_name}")
    print(best_metrics)


if __name__ == "__main__":
    train()