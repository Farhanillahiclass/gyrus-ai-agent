"""
train_model.py — trains Gyrus's own local intent classifier. Zero AI API,
zero Ollama, zero cloud calls — pure scikit-learn on your CPU, done in seconds.

Usage:
    python train_model.py
        Trains on the bundled data/intents_dataset.csv (starter set, ~100 examples).

    python train_model.py --extra path/to/kaggle_dataset.csv --text-col text --intent-col intent
        Merges in a larger dataset (e.g. one you downloaded from Kaggle) before
        training, for better accuracy and coverage. The extra CSV just needs a
        text column and a label column — name them however you like and pass
        --text-col / --intent-col to match.

Growing the training data with a real Kaggle dataset:
    1. pip install kaggle
    2. Get a free API token: https://www.kaggle.com/settings -> "Create New Token"
       (downloads kaggle.json — put it in ~/.kaggle/kaggle.json)
    3. kaggle datasets download -d <owner>/<dataset-name> -p data/ --unzip
       Any intent-labeled chatbot/conversation dataset works — search Kaggle for
       "chatbot intents dataset" or "customer support intent classification".
    4. python train_model.py --extra data/<downloaded_file>.csv --text-col <col> --intent-col <col>

Note: kaggle.com here is a DATA source, not an AI API — no model inference
happens on Kaggle's side; the CSV is just training examples for the classifier
that runs 100% locally below.
"""

import argparse
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

BASE_DATASET = Path(__file__).resolve().parent / "data" / "intents_dataset.csv"
MODEL_OUT = Path(__file__).resolve().parent / "models" / "intent_classifier.joblib"


def load_data(extra_path=None, text_col="text", intent_col="intent"):
    df = pd.read_csv(BASE_DATASET)
    if extra_path:
        extra = pd.read_csv(extra_path)
        extra = extra[[text_col, intent_col]].rename(columns={text_col: "text", intent_col: "intent"})
        df = pd.concat([df, extra], ignore_index=True)
    df = df.dropna(subset=["text", "intent"])
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"] != ""]
    return df


def train(df: pd.DataFrame):
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["intent"], test_size=0.2, random_state=42,
        stratify=df["intent"] if df["intent"].value_counts().min() > 1 else None
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    pipeline.fit(X_train, y_train)

    print("\n--- Evaluation on held-out test split ---")
    preds = pipeline.predict(X_test)
    print(classification_report(y_test, preds, zero_division=0))

    # Retrain on ALL data for the final saved model (more data = better for small datasets)
    pipeline.fit(df["text"], df["intent"])

    MODEL_OUT.parent.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_OUT)
    print(f"\nModel saved: {MODEL_OUT}")
    print(f"Trained on {len(df)} examples across {df['intent'].nunique()} intents.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--extra", help="Path to an additional CSV to merge in (e.g. a Kaggle dataset)")
    parser.add_argument("--text-col", default="text")
    parser.add_argument("--intent-col", default="intent")
    args = parser.parse_args()

    data = load_data(args.extra, args.text_col, args.intent_col)
    train(data)
