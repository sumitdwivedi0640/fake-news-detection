from typing import Dict, List

import numpy as np
try:
    import shap  # type: ignore
except Exception:  # pragma: no cover
    shap = None

from src.services.classifier import ClassifierService


class SHAPService:
    def __init__(self, classifier: ClassifierService) -> None:
        self.classifier = classifier

    def explain(self, text: str, top_k: int = 10) -> Dict[str, List[float]]:
        vectorizer = self.classifier.vectorizer
        model = self.classifier.model

        transformed = vectorizer.transform([text])
        feature_names = np.array(vectorizer.get_feature_names_out())

        try:
            if shap is not None:
                explainer = shap.LinearExplainer(model, transformed, feature_perturbation="interventional")
                shap_values = explainer.shap_values(transformed)
                class_values = shap_values[0] if isinstance(shap_values, list) else shap_values[0]
                dense_weights = np.asarray(class_values).flatten()
            else:
                raise ImportError("shap is not installed")
        except Exception:
            coeffs = np.asarray(model.coef_).flatten()
            dense_vector = transformed.toarray().flatten()
            dense_weights = coeffs * dense_vector

        non_zero_indices = np.where(transformed.toarray().flatten() > 0)[0]
        if len(non_zero_indices) == 0:
            return {"important_words": [], "weights": []}

        ranked = sorted(
            non_zero_indices,
            key=lambda idx: abs(dense_weights[idx]),
            reverse=True,
        )[:top_k]

        important_words = feature_names[ranked].tolist()
        weights = [float(dense_weights[idx]) for idx in ranked]
        return {"important_words": important_words, "weights": weights}
