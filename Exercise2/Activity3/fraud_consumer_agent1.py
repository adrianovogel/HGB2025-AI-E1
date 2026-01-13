# This agent calculates a running average for each user and flags transactions that are significantly higher than their usual behavior (e.g., $3\sigma$ outliers).

import json
import statistics
import base64
from kafka import KafkaConsumer

# Configuration
BROKER = ["localhost:9094"]
TOPIC = "dbserver1.public.transactions"
GROUP_ID = "fraud-agent-avg"

# In-memory store for user spending patterns
user_spending_profiles = {}

def parse_amount(value):
    # handles Debezium/Connect decimal formats safely
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # may be base64 for decimals
        try:
            raw = base64.b64decode(value)
            return int.from_bytes(raw, "big", signed=True) / 100
        except Exception:
            try:
                return float(value)
            except Exception:
                return None
    if isinstance(value, dict) and "value" in value:
        # sometimes { "scale": 2, "value": "..." }
        try:
            raw = base64.b64decode(value["value"])
            scale = int(value.get("scale", 2))
            return int.from_bytes(raw, "big", signed=True) / (10 ** scale)
        except Exception:
            return None
    return None

def analyze_pattern(data):
    user_id = data['user_id']
    amount = parse_amount(data.get('amount'))
    if amount is None:
        return False

    if user_id not in user_spending_profiles:
        user_spending_profiles[user_id] = []

    history = user_spending_profiles[user_id]

    # Analyze if transaction is an outlier (Need at least 3 transactions to judge)
    is_anomaly = False
    if len(history) >= 3:
        avg = statistics.mean(history)
        stdev = statistics.stdev(history) if len(history) > 1 else 0

        # If amount is > 3x the average (Simple heuristic)
        if amount > (avg * 3) and amount > 500:
            is_anomaly = True

    # Update profile
    history.append(amount)
    # Keep only last 50 transactions per user for memory efficiency
    if len(history) > 50:
        history.pop(0)

    return is_anomaly

print("🧬 Anomaly Detection Agent started.")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BROKER,
    group_id=GROUP_ID,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

for message in consumer:  # consumer is now implemented
    payload = message.value.get('payload', {})
    data = payload.get('after')

    if data:
        is_fraudulent_pattern = analyze_pattern(data)

        if is_fraudulent_pattern:
            print(f"🚨 ANOMALY DETECTED: User {data['user_id']} spent {parse_amount(data.get('amount'))} (Significantly higher than average)")
        else:
            print(f"📊 Profile updated for User {data['user_id']}")
