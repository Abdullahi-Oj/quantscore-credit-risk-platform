import time

import joblib
import shap

from app.core.config import settings


class ModelBundle:
    """
    Container for model artifacts and explainability tools.

    Loads the trained model, calibration objects, scaler,
    and initializes the SHAP explainer at application startup.
    """

    def __init__(self) -> None:
        self.load_model()
        self._init_explainer()

    def load_model(self) -> None:
        """
        Load serialized model artifacts from disk.
        """
        artifacts = joblib.load(settings.MODEL_PATH)

        self.model = artifacts["model"]
        self.calibrator = artifacts["calibrator"]
        self.scaler = artifacts["scaler"]
        self.features = artifacts["features"]
        self.sample_data = artifacts.get("sample_data", None)

        self.loaded_at = time.strftime("%Y-%m-%d %H:%M:%S")

    def _init_explainer(self) -> None:
        """
        Initialize SHAP explainer once at startup.

        TreeExplainer is fast and stable for tree-based models.
        """
        self.explainer = shap.TreeExplainer(self.model)

    def version(self) -> dict:
        """
        Return model version metadata.
        """
        return {
            "model_file": settings.MODEL_PATH,
            "loaded_at": self.loaded_at,
        }