"""
Kosha Python Client SDK

Production-ready client for the Kosha Reconciliation API with:
- Batch processing with automatic chunking
- Retry logic with exponential backoff
- Audit hash validation
- Progress tracking and error handling
"""

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class TransactionResult:
    """Result from processing a single transaction."""

    transaction_id: str
    audit_hash: str
    exception_flag: bool
    reason_code: str
    confidence: float
    explainability_features: Dict[str, Any]
    request_timestamp: str
    response_timestamp: str


@dataclass
class BatchResult:
    """Result from processing a batch of transactions."""

    batch_id: int
    total_transactions: int
    successful: int
    failed: int
    results: List[TransactionResult]
    duration_seconds: float
    throughput: float  # transactions per second


class AuditHashValidator:
    """Validates audit hash integrity for API responses."""

    @staticmethod
    def compute_audit_hash(data: Dict[str, Any]) -> str:
        """
        Compute SHA-256 audit hash matching the server-side implementation.

        Args:
            data: Transaction data dictionary

        Returns:
            SHA-256 hash as hex string
        """
        # Match server implementation: json.dumps with sort_keys=True, default=str
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    @staticmethod
    def validate_result(
        result: Dict[str, Any], original_transaction: Dict[str, Any]
    ) -> bool:
        """
        Validate that the audit hash in the result matches the original transaction.

        Args:
            result: API response result
            original_transaction: Original transaction sent to API

        Returns:
            True if audit hash is valid, False otherwise
        """
        if "audit_hash" not in result:
            return False

        # Reconstruct the data that should have been hashed
        # The server hashes the transaction input + prediction output
        expected_data = {
            **original_transaction,
            "exception_flag": result.get("exception_flag"),
            "reason_code": result.get("reason_code"),
            "confidence": result.get("confidence"),
        }

        computed_hash = AuditHashValidator.compute_audit_hash(expected_data)
        return computed_hash == result["audit_hash"]


class BatchProcessor:
    """Handles batch processing with chunking and progress tracking."""

    def __init__(
        self,
        api_url: str,
        batch_size: int = 1000,
        max_retries: int = 3,
        timeout: int = 60,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ):
        """
        Initialize batch processor.

        Args:
            api_url: Base URL of the Kosha API
            batch_size: Number of transactions per batch (max 5000)
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            progress_callback: Optional callback function(current, total)
        """
        self.api_url = api_url.rstrip("/")
        self.batch_size = min(batch_size, 5000)  # Enforce max batch size
        self.max_retries = max_retries
        self.timeout = timeout
        self.progress_callback = progress_callback

        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,  # Exponential backoff: 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def process_batch(
        self, transactions: List[Dict[str, Any]], batch_id: int = 0
    ) -> BatchResult:
        """
        Process a single batch of transactions.

        Args:
            transactions: List of transaction dictionaries
            batch_id: Batch identifier for tracking

        Returns:
            BatchResult with processing details

        Raises:
            requests.RequestException: On API communication error
        """
        start_time = time.time()
        request_timestamp = datetime.now(timezone.utc).isoformat()

        response = self.session.post(
            f"{self.api_url}/paid-api/v1/reconcile/batch",
            json=transactions,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )

        response_timestamp = datetime.now(timezone.utc).isoformat()
        duration = time.time() - start_time

        if response.status_code != 200:
            error_detail = (
                response.json().get("detail", "Unknown error")
                if response.text
                else "No response"
            )
            raise requests.RequestException(
                f"Batch {batch_id} failed with status {response.status_code}: {error_detail}"
            )

        results_json = response.json()
        results = []

        for i, (txn, result) in enumerate(zip(transactions, results_json)):
            results.append(
                TransactionResult(
                    transaction_id=txn.get("transaction_id", f"txn_{batch_id}_{i}"),
                    audit_hash=result["audit_hash"],
                    exception_flag=result["exception_flag"],
                    reason_code=result["reason_code"],
                    confidence=result["confidence"],
                    explainability_features=result.get("explainability_features", {}),
                    request_timestamp=request_timestamp,
                    response_timestamp=response_timestamp,
                )
            )

        return BatchResult(
            batch_id=batch_id,
            total_transactions=len(transactions),
            successful=len(results),
            failed=0,
            results=results,
            duration_seconds=duration,
            throughput=len(transactions) / duration if duration > 0 else 0,
        )

    def process_all(
        self, transactions: List[Dict[str, Any]], validate_audit_hash: bool = False
    ) -> Dict[str, Any]:
        """
        Process all transactions in batches.

        Args:
            transactions: List of all transactions to process
            validate_audit_hash: Whether to validate audit hashes (slower)

        Returns:
            Dictionary with processing summary and all results
        """
        total = len(transactions)
        all_results = []
        failed_batches = []
        start_time = time.time()

        # Process in batches
        for i in range(0, total, self.batch_size):
            batch_id = (i // self.batch_size) + 1
            batch = transactions[i : i + self.batch_size]

            try:
                batch_result = self.process_batch(batch, batch_id)
                all_results.extend(batch_result.results)

                # Optional audit hash validation
                if validate_audit_hash:
                    invalid_hashes = []
                    for j, result in enumerate(batch_result.results):
                        original = batch[j]
                        result_dict = {
                            "audit_hash": result.audit_hash,
                            "exception_flag": result.exception_flag,
                            "reason_code": result.reason_code,
                            "confidence": result.confidence,
                        }
                        if not AuditHashValidator.validate_result(
                            result_dict, original
                        ):
                            invalid_hashes.append(result.transaction_id)

                    if invalid_hashes:
                        print(
                            f"Warning: Batch {batch_id} has {len(invalid_hashes)} invalid audit hashes"
                        )

                # Progress callback
                if self.progress_callback:
                    self.progress_callback(i + len(batch), total)

            except Exception as e:
                failed_batches.append({"batch_id": batch_id, "error": str(e)})
                print(f"Error processing batch {batch_id}: {e}")

        total_time = time.time() - start_time

        return {
            "total_transactions": total,
            "successful": len(all_results),
            "failed": total - len(all_results),
            "failed_batches": failed_batches,
            "total_time": total_time,
            "throughput": total / total_time if total_time > 0 else 0,
            "results": all_results,
        }


class KoshaClient:
    """
    High-level client for the Kosha Reconciliation API.

    Provides simple methods for single and batch transaction processing
    with built-in error handling, retry logic, and audit validation.
    """

    def __init__(
        self,
        api_url: str = "http://127.0.0.1:8000",
        batch_size: int = 1000,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        """
        Initialize Kosha client.

        Args:
            api_url: Base URL of the Kosha API (default: http://127.0.0.1:8000)
            batch_size: Default batch size for bulk operations (default: 1000)
            max_retries: Maximum number of retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 60)
        """
        self.api_url = api_url.rstrip("/")
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.timeout = timeout

        # Configure session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.

        Returns:
            Health status dictionary

        Raises:
            requests.RequestException: On connection error
        """
        response = self.session.get(f"{self.api_url}/health", timeout=5)
        response.raise_for_status()
        return response.json()

    def reconcile_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single transaction.

        Args:
            transaction: Transaction data dictionary

        Returns:
            Inference result with audit_hash, exception_flag, etc.

        Raises:
            requests.RequestException: On API error
        """
        response = self.session.post(
            f"{self.api_url}/paid-api/v1/reconcile",
            json=transaction,
            headers={"Content-Type": "application/json"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def reconcile_batch(
        self,
        transactions: List[Dict[str, Any]],
        validate_audit_hash: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Process multiple transactions in batches.

        Args:
            transactions: List of transaction dictionaries
            validate_audit_hash: Whether to validate audit hashes (default: False)
            progress_callback: Optional callback function(current, total)

        Returns:
            Processing summary with results

        Raises:
            requests.RequestException: On API error
        """
        processor = BatchProcessor(
            api_url=self.api_url,
            batch_size=self.batch_size,
            max_retries=self.max_retries,
            timeout=self.timeout,
            progress_callback=progress_callback,
        )

        return processor.process_all(transactions, validate_audit_hash)

    def load_transactions_from_csv(
        self, file_path: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Load transactions from CSV file.

        Args:
            file_path: Path to CSV file
            limit: Maximum number of transactions to load

        Returns:
            List of transaction dictionaries
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for CSV loading. Install with: pip install pandas"
            )

        df = pd.read_csv(file_path)
        if limit:
            df = df.head(limit)

        transactions = []
        for _, row in df.iterrows():
            transaction = {
                "client_id": row.get("client_id", "UNKNOWN"),
                "transaction_id": row.get("transaction_id", ""),
                "sequence_id": int(row.get("sequence_id", 0)),
                "event_timestamp": row.get(
                    "timestamp", datetime.now(timezone.utc).isoformat()
                ),
                "execution_timestamp": row.get(
                    "timestamp", datetime.now(timezone.utc).isoformat()
                ),
                "ledger_a_amount": float(row.get("ledger_a_amount", 0.0)),
                "ledger_a_fx": float(row.get("ledger_a_fx", 1.0)),
                "ledger_a_fee": float(row.get("ledger_a_fee", 0.0)),
                "ledger_b_amount": float(row.get("ledger_b_amount", 0.0)),
                "ledger_b_fx": float(row.get("ledger_b_fx", 1.0)),
                "ledger_b_fee": float(row.get("ledger_b_fee", 0.0)),
                "currency": row.get("currency", "USD"),
                "vendor_name": row.get("vendor_name", ""),
                "counterparty_name": row.get(
                    "counterparty_name", row.get("vendor_name", "")
                ),
                "source_system_id": row.get("source_system_id", "CSV_IMPORT"),
                "context_data": {},
            }
            transactions.append(transaction)

        return transactions
