from http.server import BaseHTTPRequestHandler
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deepseek import call_deepseek, parse_json_response


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {
            "status": "ok",
            "message": "Fraud Detection API (Powered by DeepSeek AI)",
            "version": "2.0.0",
            "endpoints": {
                "POST /api": "Predict fraud probability with AI analysis",
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
                    "risk_level": "LOW/MEDIUM/HIGH",
                    "explanation": "AI-generated explanation",
                    "risk_factors": "array of risk factors"
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

        # Rule-based scoring (primary)
        risk_score = 0.0
        risk_factors = []

        if amount > 1000:
            risk_score += 0.3
            risk_factors.append(f"High transaction amount (${amount:,.2f})")
        elif amount > 500:
            risk_score += 0.15
            risk_factors.append(f"Moderate transaction amount (${amount:,.2f})")

        if num_transactions_24h > 5:
            risk_score += 0.25
            risk_factors.append(f"Unusual number of transactions ({num_transactions_24h} in 24h)")
        elif num_transactions_24h > 3:
            risk_score += 0.1

        if distance_from_home > 100:
            risk_score += 0.2
            risk_factors.append(f"Transaction far from home ({distance_from_home:.0f}km)")
        elif distance_from_home > 50:
            risk_score += 0.1

        if is_foreign:
            risk_score += 0.2
            risk_factors.append("Foreign transaction")

        if is_online:
            risk_score += 0.1
            risk_factors.append("Online transaction")

        risk_score = min(risk_score, 1.0)

        if risk_score >= 0.7:
            risk_level = "HIGH"
        elif risk_score >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        is_fraud = risk_score >= 0.5

        # Call DeepSeek for explanation
        system_prompt = """You are a fraud detection expert. Given transaction details and a risk assessment, provide a brief explanation.
Return JSON with:
- explanation: 2-3 sentence explanation of why this transaction is/isn't suspicious
- recommendation: what action to take
- confidence_note: how confident the assessment is"""

        prompt = f"""Transaction details:
- Amount: ${amount:,.2f}
- Transactions in 24h: {num_transactions_24h}
- Distance from home: {distance_from_home:.0f}km
- Foreign: {'Yes' if is_foreign else 'No'}
- Online: {'Yes' if is_online else 'No'}

Risk Score: {risk_score:.2f} ({risk_level})
Is Fraud: {is_fraud}
Risk Factors: {', '.join(risk_factors) if risk_factors else 'None'}

Provide explanation and recommendation."""

        ai_result = call_deepseek(prompt, system_prompt, max_tokens=300, temperature=0.3)
        
        explanation = ""
        recommendation = ""
        confidence_note = ""
        
        if ai_result["success"]:
            parsed = parse_json_response(ai_result["content"])
            explanation = parsed.get("explanation", "")
            recommendation = parsed.get("recommendation", "")
            confidence_note = parsed.get("confidence_note", "")

        response = {
            "fraud_probability": round(risk_score, 4),
            "is_fraud": is_fraud,
            "risk_level": risk_level,
            "risk_factors": risk_factors if risk_factors else ["No significant risk factors"],
            "explanation": explanation,
            "recommendation": recommendation,
            "confidence_note": confidence_note,
            "input": data,
            "powered_by": "DeepSeek AI + Rule Engine"
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
