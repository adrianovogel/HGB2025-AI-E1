#This agent uses a sliding window (simulated) to perform velocity checks and score the transaction
import json
from collections import deque
import time
import base64
from kafka import KafkaConsumer

# Configuration
BROKER = ["localhost:9094"]
TOPIC = "dbserver1.public.transactions"
GROUP_ID = "fraud-agent-velocity"

# Simulated In-Memory State for Velocity Checks.
user_history = {}

def parse_amount(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            raw = base64.b64decode(value)
            return int.from_bytes(raw, "big", signed=True) / 100
        except Exception:
            try:
                return float(value)
            except Exception:
                return None
    if isinstance(value, dict) and "value" in value:
        try:
            raw = base64.b64decode(value["value"])
            scale = int(value.get("scale", 2))
            return int.from_bytes(raw, "big", signed=True) / (10 ** scale)
        except Exception:
            return None
    return None

def analyze_fraud(transaction):
    user_id = transaction['user_id']
    amount = parse_amount(transaction.get('amount'))
    if amount is None:
        return 0

    # 1. Velocity Check (Recent transaction count)
    now = time.time()
    if user_id not in user_history:
        user_history[user_id] = deque()

    # Keep only last 60 seconds of history
    user_history[user_id].append(now)
    while user_history[user_id] and user_history[user_id][0] < now - 60:
        user_history[user_id].popleft()

    velocity = len(user_history[user_id])

    # 2. Heuristic Fraud Scoring
    score = 0
    if velocity > 5:
        score += 40  # Too many transactions in a minute
    if amount > 4000:
        score += 50  # High value transaction

    return score

print("Agent started. Listening for CDC events...")

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BROKER,
    group_id=GROUP_ID,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
)

for message in consumer:
    payload = message.value.get('payload', {})
    data = payload.get('after')

    if data:
        fraud_score = analyze_fraud(data)
        if fraud_score > 70:
            print(f"⚠️ HIGH FRAUD ALERT: User {data['user_id']} | Score: {fraud_score} | Amt: {parse_amount(data.get('amount'))}")
        else:
            print(f"✅ Transaction OK: {data.get('id')} (Score: {fraud_score})")
