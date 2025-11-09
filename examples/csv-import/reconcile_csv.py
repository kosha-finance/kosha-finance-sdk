#!/usr/bin/env python3
"""
CSV Import and Reconciliation Example

This example demonstrates how to:
1. Load transactions from CSV files
2. Process them in batches
3. Track progress
4. Export results to CSV
5. Generate a summary report

Usage:
    python reconcile_csv.py --input transactions.csv --output results.csv
"""

import argparse
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from kosha_client import KoshaClient, BatchProcessor


def load_transactions_from_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Load transactions from CSV file"""
    print(f"📂 Loading transactions from {csv_path}...")

    df = pd.read_csv(csv_path)
    transactions = df.to_dict('records')

    print(f"   ✓ Loaded {len(transactions)} transactions")
    return transactions


def reconcile_transactions(
    client: KoshaClient,
    transactions: List[Dict[str, Any]],
    batch_size: int = 1000
) -> List[Dict[str, Any]]:
    """Reconcile transactions in batches with progress tracking"""
    print(f"\n🔄 Reconciling {len(transactions)} transactions...")

    processor = BatchProcessor(client, batch_size=batch_size)

    def progress_callback(current: int, total: int):
        percentage = (current / total) * 100
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r   [{bar}] {current}/{total} ({percentage:.1f}%)", end='')

    results = processor.process_all(
        transactions,
        progress_callback=progress_callback,
        validate_audit_hash=True
    )

    print()  # New line after progress bar
    return results


def generate_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate reconciliation summary report"""
    total = len(results)
    matched = sum(1 for r in results if r.get('is_match'))
    unmatched = total - matched

    # Count by match type
    match_types = {}
    for result in results:
        if result.get('is_match'):
            match_type = result.get('match_type', 'unknown')
            match_types[match_type] = match_types.get(match_type, 0) + 1

    # Calculate average confidence
    confidences = [
        float(r.get('confidence_score', 0))
        for r in results
        if r.get('is_match')
    ]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0

    return {
        'total_processed': total,
        'matched': matched,
        'unmatched': unmatched,
        'match_rate': (matched / total * 100) if total > 0 else 0,
        'match_types': match_types,
        'avg_confidence': avg_confidence
    }


def export_results(
    results: List[Dict[str, Any]],
    output_path: str,
    unmatched_only: bool = False
):
    """Export results to CSV"""
    print(f"\n💾 Exporting results to {output_path}...")

    if unmatched_only:
        results = [r for r in results if not r.get('is_match')]
        print(f"   Exporting {len(results)} unmatched transactions")

    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"   ✓ Exported to {output_path}")


def print_report(report: Dict[str, Any]):
    """Print formatted reconciliation report"""
    print("\n" + "=" * 60)
    print("📊 RECONCILIATION REPORT")
    print("=" * 60)
    print(f"\nTotal Processed:  {report['total_processed']:,}")
    print(f"Matched:          {report['matched']:,} ({report['match_rate']:.1f}%)")
    print(f"Unmatched:        {report['unmatched']:,}")
    print(f"Avg Confidence:   {report['avg_confidence']:.2%}")

    if report['match_types']:
        print("\n📈 Matches by Type:")
        for match_type, count in sorted(report['match_types'].items()):
            percentage = (count / report['matched'] * 100) if report['matched'] > 0 else 0
            print(f"   {match_type:10s}  {count:5,} ({percentage:.1f}%)")

    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Reconcile transactions from CSV using Kosha Finance API'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input CSV file path'
    )
    parser.add_argument(
        '--output',
        default='results.csv',
        help='Output CSV file path (default: results.csv)'
    )
    parser.add_argument(
        '--unmatched-output',
        help='Export unmatched transactions to separate file'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Batch size for processing (default: 1000)'
    )
    parser.add_argument(
        '--api-key',
        default=os.getenv('KOSHA_API_KEY'),
        help='Kosha API key (or set KOSHA_API_KEY env var)'
    )
    parser.add_argument(
        '--base-url',
        default='https://api.kosha.finance',
        help='API base URL (default: https://api.kosha.finance)'
    )

    args = parser.parse_args()

    # Validate API key
    if not args.api_key:
        print("❌ Error: API key required. Set KOSHA_API_KEY env var or use --api-key")
        sys.exit(1)

    # Initialize client
    print("🚀 Initializing Kosha Finance client...")
    client = KoshaClient(
        api_key=args.api_key,
        base_url=args.base_url
    )

    # Health check
    try:
        health = client.health_check()
        print(f"   ✓ API Status: {health.get('status', 'OK')}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        sys.exit(1)

    # Load transactions
    try:
        transactions = load_transactions_from_csv(args.input)
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        sys.exit(1)

    # Reconcile
    try:
        results = reconcile_transactions(
            client,
            transactions,
            batch_size=args.batch_size
        )
    except Exception as e:
        print(f"❌ Error during reconciliation: {e}")
        sys.exit(1)

    # Generate and print report
    report = generate_report(results)
    print_report(report)

    # Export results
    try:
        export_results(results, args.output)

        if args.unmatched_output:
            export_results(results, args.unmatched_output, unmatched_only=True)
    except Exception as e:
        print(f"❌ Error exporting results: {e}")
        sys.exit(1)

    print("✅ Done!")


if __name__ == '__main__':
    main()
