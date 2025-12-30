import joblib
import os

# Path to your model file
model_path = "xgb_calibrated.pkl"

# Check if file exists
if not os.path.exists(model_path):
    raise FileNotFoundError(f"{model_path} not found!")

# Load artifact
artifact = joblib.load(model_path)

# Print the available keys
print("Available keys in artifact:", artifact.keys())
