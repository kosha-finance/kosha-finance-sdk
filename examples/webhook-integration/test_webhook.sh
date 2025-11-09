#!/bin/bash
#
# Test webhook endpoint with sample transaction
#

WEBHOOK_URL="${WEBHOOK_URL:-http://localhost:5000}"

echo "Testing Kosha Finance webhook integration"
echo "Webhook URL: $WEBHOOK_URL"
echo

# Test health check
echo "1. Health Check"
curl -s "$WEBHOOK_URL/health" | python -m json.tool
echo

# Test single transaction
echo "2. Single Transaction"
curl -s -X POST "$WEBHOOK_URL/webhook/transaction" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "pay_test_001",
    "amount": 100.50,
    "currency": "USD",
    "created_at": "2025-01-15T10:30:00Z",
    "description": "Test payment",
    "metadata": {}
  }' | python -m json.tool
echo

# Test batch processing
echo "3. Batch Processing"
curl -s -X POST "$WEBHOOK_URL/webhook/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "batch_001",
    "transactions": [
      {
        "payment_id": "pay_001",
        "amount": 100.50,
        "currency": "USD",
        "created_at": "2025-01-15T10:30:00Z",
        "description": "Payment 1"
      },
      {
        "payment_id": "pay_002",
        "amount": 250.00,
        "currency": "USD",
        "created_at": "2025-01-16T14:20:00Z",
        "description": "Payment 2"
      }
    ]
  }' | python -m json.tool
echo
