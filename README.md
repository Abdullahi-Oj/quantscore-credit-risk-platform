# QuantScore — Credit Risk Intelligence Platform

QuantScore is an end-to-end AI-powered credit risk platform designed for digital lenders and fintechs operating in emerging markets, with a strong focus on Africa.

The platform combines machine learning, portfolio analytics, and explainable risk modeling to support responsible lending at scale.

---

##  Key Capabilities

- **Probability of Default (PD) Modeling**
  - Supervised ML models (XGBoost, Logistic Regression)
  - Class imbalance handling (SMOTE)
  - Model calibration (Isotonic Regression)

- **Explainability & Transparency**
  - SHAP-based explanations
  - Feature contribution analysis
  - Model interpretability for risk & compliance teams

- **Portfolio Risk Analytics**
  - Default rate monitoring
  - Risk segmentation
  - Performance tracking across cohorts

- **Production API**
  - FastAPI-based inference service
  - API key authentication
  - Deployed for real-time scoring

---

##  Architecture Overview

```text
Data Ingestion → Feature Engineering → Model Training & Calibration
               ↓
        Model Explainability (SHAP)
               ↓
        FastAPI Scoring Service
               ↓
        Portfolio Monitoring & Reporting
