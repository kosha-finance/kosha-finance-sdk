"""
Batch processing example for Kosha Python Client SDK.

Demonstrates:
- Large-scale batch processing (>50K records)
- Progress tracking with callbacks
- Performance metrics
- Error handling for batch operations
"""

import sys
from datetime import UTC, datetime

# Add parent directory to path for local imports
sys.path.insert(0, "..")

from kosha_client import KoshaClient


def main():
    """Demonstrate batch processing with SDK."""
    print("=" * 60)
    print("Kosha Client SDK - Batch Processing Example")
    print("=" * 60)

    # Initialize client with batch configuration
    client = KoshaClient(
        api_url="http://127.0.0.1:8000",
        batch_size=1000,  # Process 1000 transactions per request
        max_retries=3,
        timeout=120,  # Longer timeout for large batches
    )

    # Check API health
    print("\nChecking API health...")
    try:
        health = client.health_check()
        print(f"✓ API Status: {health['status']}")
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        print("\nMake sure the API is running:")
        print("  uvicorn app.main:app --reload")
        sys.exit(1)

    # Generate sample transactions (or load from CSV)
    print("\nGenerating sample transactions...")
    num_transactions = 5000  # Start with 5K for demo
    transactions = []

    for i in range(num_transactions):
        transaction = {
            "client_id": f"BATCH_CLIENT_{i % 10}",
            "transaction_id": f"BATCH_TXN_{i:06d}",
            "sequence_id": i + 1,
            "event_timestamp": datetime.now(UTC).isoformat(),
            "execution_timestamp": datetime.now(UTC).isoformat(),
            "ledger_a_amount": 1000.0 + (i * 10),
            "ledger_a_fx": 1.2345,
            "ledger_a_fee": 10.0,
            "ledger_b_amount": 1000.0 + (i * 10),
            "ledger_b_fx": 1.2345,
            "ledger_b_fee": 10.0,
            "currency": "USD",
            "vendor_name": f"Vendor_{i % 100}",
            "counterparty_name": f"Counter_{i % 100}",
            "source_system_id": "BATCH_DEMO",
            "context_data": {"batch_index": i},
        }
        transactions.append(transaction)

    print(f"✓ Generated {len(transactions):,} transactions")

    # Progress tracking callback
    def progress_callback(current, total):
        percent = (current / total) * 100
        print(f"  Progress: {current:,}/{total:,} ({percent:.1f}%)")

    # Process batch with progress tracking
    print(f"\nProcessing {len(transactions):,} transactions...")
    print("This may take a few minutes...\n")

    try:
        results = client.reconcile_batch(
            transactions,
            validate_audit_hash=False,  # Set to True for validation
            progress_callback=progress_callback,
        )

        # Display results
        print("\n" + "=" * 60)
        print("Processing Summary")
        print("=" * 60)
        print(f"Total Transactions:  {results['total_transactions']:,}")
        print(f"Successful:          {results['successful']:,}")
        print(f"Failed:              {results['failed']:,}")
        print(f"Total Time:          {results['total_time']:.2f} seconds")
        print(f"Throughput:          {results['throughput']:.0f} transactions/sec")

        if results["failed_batches"]:
            print(f"\nFailed Batches: {len(results['failed_batches'])}")
            for fb in results["failed_batches"]:
                print(f"  - Batch {fb['batch_id']}: {fb['error']}")

        # Sample results
        if results["results"]:
            print("\nSample Results (first 3):")
            for i, result in enumerate(results["results"][:3]):
                print(f"\n  Transaction {i + 1}:")
                print(f"    ID: {result.transaction_id}")
                print(f"    Exception: {result.exception_flag}")
                print(f"    Reason: {result.reason_code}")
                print(f"    Confidence: {result.confidence:.2%}")
                print(f"    Audit Hash: {result.audit_hash[:16]}...")

        print("\n" + "=" * 60)
        print("✓ Batch processing completed successfully")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Batch processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
