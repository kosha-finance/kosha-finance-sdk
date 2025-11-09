"""
Audit hash validation example for Kosha Python Client SDK.

Demonstrates:
- Computing audit hashes
- Validating API responses
- End-to-end integrity checking
- Detecting tampered responses
"""

import sys
from datetime import UTC, datetime

# Add parent directory to path for local imports
sys.path.insert(0, "..")

from kosha_client import AuditHashValidator, KoshaClient


def main():
    """Demonstrate audit hash validation."""
    print("=" * 60)
    print("Kosha Client SDK - Audit Hash Validation Example")
    print("=" * 60)

    # Initialize client
    client = KoshaClient(api_url="http://127.0.0.1:8000")

    # Check API health
    print("\nChecking API health...")
    try:
        health = client.health_check()
        print(f"✓ API Status: {health['status']}")
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        sys.exit(1)

    # Test 1: Single transaction with manual validation
    print("\n" + "=" * 60)
    print("Test 1: Manual Audit Hash Validation")
    print("=" * 60)

    transaction = {
        "client_id": "AUDIT_TEST",
        "transaction_id": "AUDIT_TXN_001",
        "sequence_id": 1,
        "event_timestamp": datetime.now(UTC).isoformat(),
        "execution_timestamp": datetime.now(UTC).isoformat(),
        "ledger_a_amount": 1000.0,
        "ledger_a_fx": 1.0,
        "ledger_a_fee": 5.0,
        "ledger_b_amount": 1000.0,
        "ledger_b_fx": 1.0,
        "ledger_b_fee": 5.0,
        "currency": "USD",
        "vendor_name": "Test Vendor",
        "counterparty_name": "Test Counter",
        "source_system_id": "AUDIT_TEST",
        "context_data": {},
    }

    print("\nProcessing transaction...")
    result = client.reconcile_transaction(transaction)
    print(f"✓ Received result with audit hash: {result['audit_hash'][:16]}...")

    print("\nValidating audit hash...")
    is_valid = AuditHashValidator.validate_result(result, transaction)
    if is_valid:
        print("✓ Audit hash is VALID - response integrity confirmed")
    else:
        print("✗ Audit hash is INVALID - response may be tampered")

    # Test 2: Batch processing with validation
    print("\n" + "=" * 60)
    print("Test 2: Batch Processing with Audit Validation")
    print("=" * 60)

    # Generate test batch
    batch_size = 100
    transactions = []
    for i in range(batch_size):
        txn = {
            "client_id": f"AUDIT_CLIENT_{i % 5}",
            "transaction_id": f"AUDIT_TXN_{i:04d}",
            "sequence_id": i + 1,
            "event_timestamp": datetime.now(UTC).isoformat(),
            "execution_timestamp": datetime.now(UTC).isoformat(),
            "ledger_a_amount": 1000.0 + i,
            "ledger_a_fx": 1.0,
            "ledger_a_fee": 5.0,
            "ledger_b_amount": 1000.0 + i,
            "ledger_b_fx": 1.0,
            "ledger_b_fee": 5.0,
            "currency": "USD",
            "vendor_name": f"Vendor_{i}",
            "counterparty_name": f"Counter_{i}",
            "source_system_id": "AUDIT_TEST",
            "context_data": {"index": i},
        }
        transactions.append(txn)

    print(f"\nProcessing {batch_size} transactions with audit validation...")
    print("(This adds ~10% processing overhead)\n")

    results = client.reconcile_batch(
        transactions,
        validate_audit_hash=True,  # Enable validation
        progress_callback=lambda c, t: print(f"  Progress: {c}/{t}"),
    )

    print("\n" + "=" * 60)
    print("Batch Validation Summary")
    print("=" * 60)
    print(f"Total Transactions:  {results['total_transactions']}")
    print(f"Successful:          {results['successful']}")
    print(f"Failed:              {results['failed']}")

    # Manual validation of all results
    print("\nPerforming comprehensive audit hash validation...")
    valid_count = 0
    invalid_count = 0

    for i, result_obj in enumerate(results["results"]):
        original = transactions[i]
        result_dict = {
            "audit_hash": result_obj.audit_hash,
            "exception_flag": result_obj.exception_flag,
            "reason_code": result_obj.reason_code,
            "confidence": result_obj.confidence,
        }
        if AuditHashValidator.validate_result(result_dict, original):
            valid_count += 1
        else:
            invalid_count += 1
            print(f"  ✗ Invalid hash for transaction: {result_obj.transaction_id}")

    print("\nValidation Results:")
    print(f"  ✓ Valid:   {valid_count}/{len(results['results'])}")
    print(f"  ✗ Invalid: {invalid_count}/{len(results['results'])}")

    if invalid_count == 0:
        print("\n✓ All audit hashes validated successfully!")
        print("  Response integrity confirmed for all transactions")
    else:
        print(f"\n⚠ Warning: {invalid_count} invalid audit hashes detected")

    # Test 3: Demonstrate hash computation
    print("\n" + "=" * 60)
    print("Test 3: Manual Hash Computation")
    print("=" * 60)

    sample_data = {
        "client_id": "DEMO",
        "transaction_id": "DEMO_001",
        "amount": 1000.0,
        "exception_flag": False,
        "reason_code": "NONE",
        "confidence": 0.95,
    }

    computed_hash = AuditHashValidator.compute_audit_hash(sample_data)
    print(f"\nSample Data: {sample_data}")
    print(f"Computed Hash: {computed_hash}")
    print("\n✓ SHA-256 hash computed using same algorithm as server")

    print("\n" + "=" * 60)
    print("✓ Audit hash validation examples completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
