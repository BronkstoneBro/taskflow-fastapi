import pickle
import os
from typing import Optional


class PriorityPredictor:
    def __init__(self):
        self.model: Optional[object] = None
        self.load_model()

    def load_model(self):
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "models",
            "priority_classifier.pkl",
        )

        if os.path.exists(model_path):
            try:
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                print(f"Model loaded from: {model_path}")
            except Exception as e:
                print(f"Failed to load model: {e}. Falling back to heuristic predictor.")
                self.model = None
        else:
            print(f"Model not found at: {model_path}")
            print("Please run ml/train_model.py first to train the model")

    def predict(self, task_description: str) -> str:
        if self.model is None:
            text = (task_description or "").lower()
            high_keywords = [
                "critical",
                "security",
                "vulnerability",
                "crash",
                "production",
                "optimize",
                "database",
                "api",
                "authentication",
            ]
            is_high = any(k in text for k in high_keywords)
            return "high" if is_high else "low"

        try:
            prediction = self.model.predict([task_description])[0]
            return prediction
        except Exception as e:
            print(f"Prediction error: {e}")
            return "Error in prediction"

    def predict_proba(self, task_description: str) -> dict:
        if self.model is None:
            pred = self.predict(task_description)
            if pred == "high":
                return {"high": 0.8, "low": 0.2}
            return {"high": 0.2, "low": 0.8}

        try:
            probabilities = self.model.predict_proba([task_description])[0]
            classes = self.model.classes_

            return dict(zip(classes, probabilities))
        except Exception as e:
            print(f"Prediction error: {e}")
            return {"error": "Error in prediction"}
