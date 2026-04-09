import pickle
from pathlib import Path
from typing import Dict

import numpy as np

from src.core.logger import logger

MODEL_PATH = Path("models/model.pkl")
VECTORIZER_PATH = Path("models/vectorizer.pkl")


class ClassifierService:
    def __init__(self) -> None:
        if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
            raise FileNotFoundError(
                "Model/vectorizer not found. Train model first to create models/model.pkl and models/vectorizer.pkl."
            )
        with MODEL_PATH.open("rb") as model_file:
            self.model = pickle.load(model_file)
        with VECTORIZER_PATH.open("rb") as vectorizer_file:
            self.vectorizer = pickle.load(vectorizer_file)
        logger.info("ClassifierService initialized.")

    def predict(self, text: str) -> Dict[str, float]:
        vec = self.vectorizer.transform([text])
        prediction = int(self.model.predict(vec)[0])

        confidence = 0.5
        try:
            prob = self.model.predict_proba(vec)[0]
            confidence = float(np.max(prob))
        except Exception as exc:
            logger.warning("predict_proba failed, using decision fallback: %s", exc)
            try:
                decision = float(self.model.decision_function(vec)[0])
                confidence = float(1.0 / (1.0 + np.exp(-abs(decision))))
            except Exception as inner_exc:
                logger.warning("decision_function fallback failed: %s", inner_exc)
                confidence = 0.5

        return {
            "prediction": "REAL" if prediction == 1 else "FAKE",
            "confidence": confidence,
        }
