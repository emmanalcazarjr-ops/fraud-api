# Fraud Detection API

Serverless API for detecting fraudulent transactions.

## Endpoint

**POST** `/api`

### Request Body
```json
{
  "amount": 1500,
  "num_transactions_24h": 8,
  "distance_from_home": 150,
  "is_foreign": 1,
  "is_online": 0
}
```

### Response
```json
{
  "fraud_probability": 0.85,
  "is_fraud": true,
  "risk_level": "HIGH",
  "input": { ... }
}
```

## Deploy
Push to GitHub and connect to Vercel.
