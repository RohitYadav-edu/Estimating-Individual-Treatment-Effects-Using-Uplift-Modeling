# Uplift Modeling + Serverless Deployment (AWS Lambda + API Gateway)

This project builds an **uplift model** (a.k.a. conditional treatment effect / CATE) to decide **who should receive a treatment** (ad/coupon) by estimating:

\[
uplift(x) = P(Y=1 \mid X=x, T=1) - P(Y=1 \mid X=x, T=0)
\]

Then it deploys the model as a **serverless inference API** using **AWS Lambda (container image)** + **API Gateway**.

---

## What is Uplift Modeling (in one line)
Classification predicts **who will convert**.  
Uplift predicts **who will convert *because* of the treatment**.

---

## Dataset
Using the Criteo uplift dataset (features are anonymized):
- Features: `f0 ... f11`
- Treatment: `treatment` (0/1)
- Outcome: `visit` (0/1)

> Note: The feature meanings are intentionally anonymized by Criteo, but they remain predictive and usable for uplift modeling.

---

## Modeling Approach
### Baseline: T-Learner
Train two models:
- **Treated model** learns: `P(Y=1 | X, T=1)`
- **Control model** learns: `P(Y=1 | X, T=0)`

Inference:
- `p_treated = model_treated.predict_proba(X)`
- `p_control = model_control.predict_proba(X)`
- `uplift = p_treated - p_control`

### Evaluation
Evaluated using uplift metrics (e.g., Qini / AUUC) to measure whether ranking users by predicted uplift improves realized lift.

---

## Deployment Architecture
**Train → Export → Deploy → Serve**
1. Train uplift model locally / in notebooks
2. Export bundle to `models/uplift_tlearner_bundle.joblib`
3. Build Docker image (Lambda Python 3.12 base)
4. Push image to **Amazon ECR**
5. Create **AWS Lambda** from the image
6. Expose endpoint using **API Gateway**: `POST /predict`

---

## Live Endpoint
API Gateway (stage):
- Base: `https://b0t5ntje2g.execute-api.eu-north-1.amazonaws.com/prod`
- Predict: `POST https://b0t5ntje2g.execute-api.eu-north-1.amazonaws.com/prod/predict`

---

## API Contract

### Request
Send a JSON body with `instances` (list of feature dictionaries):

```json
{
  "instances": [
    {
      "f0": 1, "f1": 2, "f2": 3, "f3": 4,
      "f4": 5, "f5": 6, "f6": 7, "f7": 8,
      "f8": 9, "f9": 10, "f10": 11, "f11": 12
    }
  ]
}
---

### Response

```json
{
  "predictions": [
    {"p_treated": 0.12, "p_control": 0.08, "uplift": 0.04}
  ],
  "model": "tlearner_logreg_v1",
  "n": 1
}

---

## Quick Test CURL

curl -s -X POST "https://b0t5ntje2g.execute-api.eu-north-1.amazonaws.com/prod/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      {"f0": 1, "f1": 2, "f2": 3, "f3": 4, "f4": 5, "f5": 6, "f6": 7, "f7": 8, "f8": 9, "f9": 10, "f10": 11, "f11": 12}
    ]
  }'

