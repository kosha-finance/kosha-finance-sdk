"""
CSV import example for Kosha Python Client SDK.

Demonstrates:
- Loading transactions from CSV files
- Processing large datasets (50K+ records)
- Progress tracking
- Performance benchmarking
"""

import sys
from pathlib import Path

# Add parent directory to path for local imports
sys.path.insert(0, "..")

from kosha_client import KoshaClient


def main():
    """Demonstrate CSV import and processing."""
    print("=" * 60)
    print("Kosha Client SDK - CSV Import Example")
    print("=" * 60)

    # Initialize client
    client = KoshaClient(
        api_url="http://127.0.0.1:8000", batch_size=1000, max_retries=3, timeout=120
    )

    # Check API health
    print("\nChecking API health...")
    try:
        health = client.health_check()
        print(f"✓ API Status: {health['status']}")
    except Exception as e:
        print(f"✗ Cannot connect to API: {e}")
        sys.exit(1)

    # Find data file
    # Look in project root data directory
    data_file = (
        Path(__file__).parent.parent.parent.parent
        / "data"
        / "synthetic_transactions.csv"
    )

    if not data_file.exists():
        print(f"\n✗ Data file not found: {data_file}")
        print("\nPlease generate synthetic data first:")
        print("  python scripts/data_generation.py")
        sys.exit(1)

    print(f"\n✓ Found data file: {data_file}")

    # Load transactions from CSV
    print("\nLoading transactions from CSV...")
    num_records = 50000  # Load 50K records for production-scale testing

    try:
        transactions = client.load_transactions_from_csv(
            str(data_file), limit=num_records
        )
        print(f"✓ Loaded {len(transactions):,} transactions from CSV")
    except ImportError:
        print("\n✗ pandas is required for CSV loading")
        print("  Install with: pip install pandas")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Failed to load CSV: {e}")
        sys.exit(1)

    # Progress tracking
    def progress_callback(current, total):
        percent = (current / total) * 100
        batches_done = current // 1000
        total_batches = (total + 999) // 1000
        print(
            f"  Batch {batches_done}/{total_batches}: {current:,}/{total:,} ({percent:.1f}%)"
        )

    # Process transactions
    print(f"\nProcessing {len(transactions):,} transactions...")
    print("This will take several minutes for 50K records...\n")

    try:
        results = client.reconcile_batch(
            transactions, validate_audit_hash=False, progress_callback=progress_callback
        )

        # Display results
        print("\n" + "=" * 60)
        print("CSV Processing Summary")
        print("=" * 60)
        print(f"Source File:         {data_file.name}")
        print(f"Total Transactions:  {results['total_transactions']:,}")
        print(f"Successful:          {results['successful']:,}")
        print(f"Failed:              {results['failed']:,}")
        print(f"Total Time:          {results['total_time']:.2f} seconds")
        print(f"Throughput:          {results['throughput']:.0f} transactions/sec")

        # Success rate
        success_rate = (results["successful"] / results["total_transactions"]) * 100
        print(f"Success Rate:        {success_rate:.2f}%")

        # Failed batches
        if results["failed_batches"]:
            print(f"\n⚠ Failed Batches: {len(results['failed_batches'])}")
            for fb in results["failed_batches"][:5]:  # Show first 5
                print(f"  - Batch {fb['batch_id']}: {fb['error']}")

        # Exception statistics
        if results["results"]:
            total_with_exceptions = sum(
                1 for r in results["results"] if r.exception_flag
            )
            exception_rate = (total_with_exceptions / len(results["results"])) * 100
            print("\nException Statistics:")
            print(
                f"  Total Exceptions:  {total_with_exceptions:,} ({exception_rate:.2f}%)"
            )

            # Count by reason code
            reason_codes = {}
            for r in results["results"]:
                code = r.reason_code
                reason_codes[code] = reason_codes.get(code, 0) + 1

            print("  Reason Codes:")
            for code, count in sorted(
                reason_codes.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                print(f"    {code}: {count:,}")

        print("\n" + "=" * 60)
        print("✓ CSV import and processing completed successfully")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Processing failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
