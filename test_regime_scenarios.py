import sys
sys.path.insert(0, ".")

import numpy as np
import pandas as pd
from app.services.regime_detection.regimes import RegimeDetector

detector = RegimeDetector()

scenarios = {
    "Calm market   (vol=0.005)": 0.005,
    "Moderate market (vol=0.015)": 0.015,
    "Crisis market  (vol=0.040)": 0.040,
}

for label, target_vol in scenarios.items():
    # Generate returns that produce the target volatility
    returns = np.random.normal(0.0005, target_vol, 100)
    df      = pd.DataFrame({"returns": returns})
    result  = detector.detect(df)

    print(f"\n{label}")
    print(f"  regime     : {result['regime']}")
    print(f"  volatility : {result['volatility']}")
    print(f"  risk_level : {result['risk_level']}")
    print(f"  normal     : {result['market_state_probability']['normal']}")
    print(f"  stress     : {result['market_state_probability']['stress']}")