
# QuantScore — Credit Risk Intelligence Platform

QuantScore is an end-to-end AI-powered credit risk platform designed for digital lenders and fintechs operating in emerging markets, with a strong focus on Africa.

The platform combines machine learning, portfolio analytics, and explainable risk modeling to support **responsible, data-driven lending decisions at scale**.

---

##  Key Capabilities

### Probability of Default (PD) Modeling
- Supervised ML models (XGBoost, Logistic Regression)
- Class imbalance handling (SMOTE)
- Model calibration using Isotonic Regression

### Explainability & Transparency
- SHAP-based model explanations
- Feature contribution analysis
- Designed for risk, compliance, and audit teams

### Portfolio Risk Analytics
- Default rate monitoring
- Risk segmentation
- Performance tracking across cohorts

### Production API
- FastAPI-based inference service
- API key authentication
- Deployed for real-time scoring demonstrations

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

 Live Deployment

API Endpoint (Render):
To be added

The platform is deployed on Render for production-style testing and demonstration of real-time credit scoring workflows.

 Tech Stack

Languages: Python

ML & Statistics: Scikit-learn, XGBoost, Statsmodels

Explainability: SHAP

Backend: FastAPI

Data: Pandas, NumPy

Deployment: Render

Version Control: Git & GitHub

 Use Cases

Digital lenders & fintechs

MSME lending platforms

BNPL providers

Credit risk & analytics teams

 Project Status

This repository represents an actively evolving credit risk system used for:

Portfolio simulation

Risk strategy testing

Production-style deployment demonstrations

Note: Current experiments use simulated and proxy datasets designed to mirror real-world lending behavior.
The system architecture is built to support seamless transition to production data sources.

 Project Walkthrough

This platform simulates a real-world credit risk system used by digital lenders.

1️ Data Ingestion

Simulated and/or historical loan-level data

Feature inputs structured to reflect real lending pipelines

2️ Feature Engineering

Income & transaction stability metrics

Behavioral ratios (e.g. spend-to-income, utilization)

Early stress indicators prior to default

3️ Modeling

Logistic regression for baseline interpretability

Gradient-boosted models (XGBoost) for predictive performance

Probability of Default (PD) estimation

4️ Calibration & Evaluation

Isotonic calibration

AUC, KS, Brier score

Portfolio-level validation metrics

5️ Explainability

SHAP-based feature attribution

Transparent decision logic for risk teams

6️ Deployment

FastAPI backend

Deployed on Render for production-style testing

 Author

Abdullahi O. Aliyu
MSc Financial Engineering
Certified Data Scientist — WorldQuant University
