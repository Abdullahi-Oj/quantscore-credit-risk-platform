import joblib
from app.config import MODEL_PATH
import time

class ModelBundle:
    def __init__(self):
        self.load_model()

    def load_model(self):
        artifacts = joblib.load(MODEL_PATH)
        self.model = artifacts["model"]
        self.calibrator = artifacts["calibrator"]
        self.scaler = artifacts["scaler"]
        self.features = artifacts["features"]
        self.loaded_at = time.strftime("%Y-%m-%d %H:%M:%S")

    def version(self):
        return {
            "model_file": MODEL_PATH,  # uses centralized path from config.py
            "loaded_at": self.loaded_at
        }
