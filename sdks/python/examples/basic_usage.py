"""
Basic usage example for Kosha Python Client SDK.

Demonstrates:
- Client initialization
- Health check
- Single transaction processing
- Basic error handling
"""

import sys
from datetime import UTC, datetime

# Add parent directory to path for local imports
sys.path.insert(0, "..")

from kosha_client import KoshaClient


def main():
    """Demonstrate basic SDK usage."""
    print("=" * 60)
    print("Kosha Client SDK - Basic Usage Example")
    print("=" * 60)

    # Initialize client
    client = KoshaClient(api_url="http://127.0.0.1:8000", timeout=30)

    # 1. Health Check
    print("\n1. Checking API health...")
    try:
        health = client.health_check()
        print(f"   ✓ API Status: {health['status']}")
        print(f"   ✓ Model Loaded: {health.get('model_loaded', 'unknown')}")
    except Exception as e:
        print(f"   ✗ Health check failed: {e}")
        print("\n   Make sure the API is running:")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)

    # 2. Process a single transaction
    print("\n2. Processing single transaction...")
    transaction = {
        "client_id": "DEMO_CLIENT",
        "transaction_id": "DEMO_TXN_001",
        "sequence_id": 1,
        "event_timestamp": datetime.now(UTC).isoformat(),
        "execution_timestamp": datetime.now(UTC).isoformat(),
        "ledger_a_amount": 1000.0,
        "ledger_a_fx": 1.2345,
        "ledger_a_fee": 10.0,
        "ledger_b_amount": 1000.0,
        "ledger_b_fx": 1.2345,
        "ledger_b_fee": 10.0,
        "currency": "USD",
        "vendor_name": "Acme Corporation",
        "counterparty_name": "Acme Corporation",
        "source_system_id": "DEMO_SYSTEM",
        "context_data": {"demo": True},
    }

    try:
        result = client.reconcile_transaction(transaction)
        print("   ✓ Transaction processed successfully")
        print(f"   ✓ Transaction ID: {transaction['transaction_id']}")
        print(f"   ✓ Exception Flag: {result['exception_flag']}")
        print(f"   ✓ Reason Code: {result['reason_code']}")
        print(f"   ✓ Confidence: {result['confidence']:.2%}")
        print(f"   ✓ Audit Hash: {result['audit_hash'][:16]}...")
    except Exception as e:
        print(f"   ✗ Transaction processing failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ Basic usage example completed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
