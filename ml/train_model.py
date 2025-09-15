import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import os


def train_priority_classifier():
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "tasks.csv"
    )
    models_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

    if not os.path.exists(models_path):
        os.makedirs(models_path)

    df = pd.read_csv(data_path)

    X = df["task_description"]
    y = df["priority"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=1000, stop_words="english", lowercase=True
                ),
            ),
            ("classifier", MultinomialNB()),
        ]
    )

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Model accuracy: {accuracy:.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    model_path = os.path.join(models_path, "priority_classifier.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)

    print(f"\nModel saved to: {model_path}")
    return pipeline


if __name__ == "__main__":
    train_priority_classifier()
