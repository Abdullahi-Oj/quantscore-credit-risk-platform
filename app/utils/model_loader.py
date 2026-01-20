import joblib
import time
import shap
from app.config import MODEL_PATH


class ModelBundle:
    def __init__(self):
        self.load_model()
        self._init_explainer()

    def load_model(self):
        artifacts = joblib.load(MODEL_PATH)
        self.model = artifacts["model"]
        self.calibrator = artifacts["calibrator"]
        self.scaler = artifacts["scaler"]
        self.features = artifacts["features"]
        self.loaded_at = time.strftime("%Y-%m-%d %H:%M:%S")

    def _init_explainer(self):
        """
        Initialize SHAP explainer once at startup.
        TreeExplainer is fast and stable for tree-based models.
        """
        self.explainer = shap.TreeExplainer(self.model)

    def version(self):
        return {
            "model_file": MODEL_PATH,
            "loaded_at": self.loaded_at
        }
