#!/usr/bin/env bash
set -euo pipefail

# Deployed API endpoint (API Gateway)
INVOKE_URL="https://b0t5ntje2g.execute-api.eu-north-1.amazonaws.com/prod/predict"

echo "==> Testing endpoint: ${INVOKE_URL}"
echo

curl -s -X POST "${INVOKE_URL}" \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [
      {
        "f0": 1, "f1": 2, "f2": 3, "f3": 4,
        "f4": 5, "f5": 6, "f6": 7, "f7": 8,
        "f8": 9, "f9": 10, "f10": 11, "f11": 12
      }
    ]
  }' | python3 -m json.tool

echo
echo "Done."
