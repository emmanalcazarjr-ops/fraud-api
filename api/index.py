from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "status": "ok",
            "message": "Fraud Detection API",
            "version": "1.0.0",
            "endpoints": {
                "POST /api": "Predict fraud probability",
                "input": {
                    "amount": "float - Transaction amount",
                    "num_transactions_24h": "int - Transactions in last 24h",
                    "distance_from_home": "float - Distance from home (km)",
                    "is_foreign": "int - 1 if foreign, 0 otherwise",
                    "is_online": "int - 1 if online, 0 otherwise"
                },
                "output": {
                    "fraud_probability": "float 0-1",
                    "is_fraud": "bool",
                    "risk_level": "LOW/MEDIUM/HIGH"
                }
            }
        }

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        amount = float(data.get('amount', 100))
        num_transactions_24h = int(data.get('num_transactions_24h', 3))
        distance_from_home = float(data.get('distance_from_home', 10))
        is_foreign = int(data.get('is_foreign', 0))
        is_online = int(data.get('is_online', 0))

        risk_score = 0.0

        if amount > 1000:
            risk_score += 0.3
        elif amount > 500:
            risk_score += 0.15

        if num_transactions_24h > 5:
            risk_score += 0.25
        elif num_transactions_24h > 3:
            risk_score += 0.1

        if distance_from_home > 100:
            risk_score += 0.2
        elif distance_from_home > 50:
            risk_score += 0.1

        if is_foreign:
            risk_score += 0.2

        if is_online:
            risk_score += 0.1

        risk_score = min(risk_score, 1.0)

        if risk_score >= 0.7:
            risk_level = "HIGH"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        is_fraud = risk_score >= 0.5

        response = {
            "fraud_probability": round(risk_score, 4),
            "is_fraud": is_fraud,
            "risk_level": risk_level,
            "input": data
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
