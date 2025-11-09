#!/usr/bin/env python3
"""
Flask Webhook Integration Example

Real-time transaction reconciliation via webhook endpoint.
This example shows how to integrate Kosha Finance API with payment processors.

Usage:
    export KOSHA_API_KEY="your_api_key"
    python flask_webhook.py

Then send POST requests to http://localhost:5000/webhook/transaction
"""

import os
from flask import Flask, request, jsonify
from kosha_client import KoshaClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Kosha client
KOSHA_API_KEY = os.getenv('KOSHA_API_KEY')
if not KOSHA_API_KEY:
    raise ValueError("KOSHA_API_KEY environment variable not set")

client = KoshaClient(
    api_key=KOSHA_API_KEY,
    base_url=os.getenv('KOSHA_API_URL', 'https://api.kosha.finance')
)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        kosha_health = client.health_check()
        return jsonify({
            'status': 'healthy',
            'kosha_api': kosha_health.get('status', 'unknown')
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@app.route('/webhook/transaction', methods=['POST'])
def process_transaction():
    """
    Webhook endpoint for real-time transaction reconciliation

    Expected payload:
    {
        "payment_id": "pay_123",
        "amount": 100.50,
        "currency": "USD",
        "created_at": "2025-01-15T10:30:00Z",
        "description": "Payment from customer",
        "metadata": {...}
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.json
        logger.info(f"Received transaction: {data.get('payment_id')}")

        # Transform payment processor data to Kosha format
        transaction = {
            "amount": data["amount"],
            "currency": data["currency"],
            "transaction_date": data["created_at"].split('T')[0],  # Extract date
            "description": data.get("description", ""),
            "reference_id": data["payment_id"]
        }

        # Reconcile immediately
        result = client.reconcile_transaction(transaction)

        if result['is_match']:
            logger.info(
                f"Transaction {data['payment_id']} matched "
                f"(type: {result['match_type']}, "
                f"confidence: {result['confidence_score']})"
            )

            # Here you would update your database
            # update_payment_status(
            #     payment_id=data["payment_id"],
            #     matched=True,
            #     match_type=result['match_type'],
            #     confidence=result['confidence_score']
            # )

            return jsonify({
                "status": "matched",
                "match_type": result['match_type'],
                "confidence": result['confidence_score'],
                "match_id": result.get('match_id')
            }), 200
        else:
            logger.warning(f"Transaction {data['payment_id']} unmatched")

            # Flag for manual review
            # flag_for_review(data["payment_id"])

            return jsonify({
                "status": "requires_review",
                "message": "No matching transaction found"
            }), 200

    except KeyError as e:
        logger.error(f"Missing required field: {e}")
        return jsonify({
            'error': f'Missing required field: {e}'
        }), 400
    except Exception as e:
        logger.error(f"Error processing transaction: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@app.route('/webhook/batch', methods=['POST'])
def process_batch():
    """
    Webhook endpoint for batch transaction processing

    Expected payload:
    {
        "batch_id": "batch_123",
        "transactions": [...]
    }
    """
    try:
        data = request.json
        transactions = data.get('transactions', [])

        if not transactions:
            return jsonify({'error': 'No transactions provided'}), 400

        logger.info(f"Processing batch {data.get('batch_id')} with {len(transactions)} transactions")

        # Transform and reconcile
        kosha_transactions = [
            {
                "amount": txn["amount"],
                "currency": txn["currency"],
                "transaction_date": txn["created_at"].split('T')[0],
                "description": txn.get("description", ""),
                "reference_id": txn["payment_id"]
            }
            for txn in transactions
        ]

        results = client.batch_reconcile(kosha_transactions)

        # Summarize results
        matched = sum(1 for r in results if r.get('is_match'))
        unmatched = len(results) - matched

        logger.info(
            f"Batch {data.get('batch_id')} complete: "
            f"{matched} matched, {unmatched} unmatched"
        )

        return jsonify({
            "batch_id": data.get('batch_id'),
            "total": len(results),
            "matched": matched,
            "unmatched": unmatched,
            "results": results
        }), 200

    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


if __name__ == '__main__':
    # Check API connectivity
    try:
        health = client.health_check()
        logger.info(f"Kosha API status: {health.get('status', 'OK')}")
    except Exception as e:
        logger.error(f"Failed to connect to Kosha API: {e}")
        exit(1)

    # Start server
    logger.info("Starting webhook server on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
