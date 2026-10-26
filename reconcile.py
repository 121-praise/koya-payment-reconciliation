#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""

import json
from datetime import datetime
from decimal import Decimal


def parse_ts(value):
    # Timestamps look like 2026-09-21T15:30:26Z (UTC).
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")


def parse_amount(value):
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    return Decimal(str(value))  


latest = {}  # txn_id -> (ts, status, amount)

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
            txn_id = event.get("txn_id")
            if not txn_id:
                continue
            ts = parse_ts(event["ts"])
            status = event["status"]
            amount = parse_amount(event["amount"])
        except (ValueError, KeyError, TypeError, AttributeError, ArithmeticError):
            continue  

        if txn_id not in latest or ts > latest[txn_id][0]:
            latest[txn_id] = (ts, status, amount)

total = Decimal(0)
count = 0
for ts, status, amount in latest.values():
    if status == "success":
        total += amount
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{int(total.quantize(Decimal('1'), rounding='ROUND_HALF_UP'))}")
