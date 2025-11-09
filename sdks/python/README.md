# Kosha Python Client SDK

Production-ready Python client for the Kosha Reconciliation API.

## Features

- **Batch Processing**: Automatic chunking of large datasets with configurable batch sizes
- **Retry Logic**: Built-in exponential backoff for failed requests
- **Audit Hash Validation**: Optional cryptographic verification of API responses
- **Progress Tracking**: Callback support for monitoring long-running operations
- **Error Handling**: Comprehensive error handling and reporting

## Installation

```bash
pip install -e ./client_sdk/python
```

For CSV file support:
```bash
pip install -e "./client_sdk/python[csv]"
```

## Quick Start

```python
from kosha_client import KoshaClient

# Initialize client
client = KoshaClient(
    api_url="http://localhost:8000",
    batch_size=1000,
    max_retries=3,
    timeout=60
)

# Check API health
health = client.health_check()
print(f"API Status: {health['status']}")

# Process a single transaction
transaction = {
    "client_id": "CLIENT_001",
    "transaction_id": "TXN_12345",
    "sequence_id": 1,
    "event_timestamp": "2024-01-15T10:30:00Z",
    "execution_timestamp": "2024-01-15T10:30:00Z",
    "ledger_a_amount": 1000.0,
    "ledger_a_fx": 1.0,
    "ledger_a_fee": 5.0,
    "ledger_b_amount": 1000.0,
    "ledger_b_fx": 1.0,
    "ledger_b_fee": 5.0,
    "currency": "USD",
    "vendor_name": "Acme Corp",
    "counterparty_name": "Acme Corp",
    "source_system_id": "SAP",
    "context_data": {}
}

result = client.reconcile_transaction(transaction)
print(f"Result: {result['reason_code']} (confidence: {result['confidence']})")
print(f"Audit Hash: {result['audit_hash']}")
```

## Batch Processing

```python
# Load transactions from CSV
transactions = client.load_transactions_from_csv(
    "data/synthetic_transactions.csv",
    limit=50000
)

# Process with progress tracking
def progress_callback(current, total):
    print(f"Progress: {current}/{total} ({current/total*100:.1f}%)")

results = client.reconcile_batch(
    transactions,
    validate_audit_hash=True,
    progress_callback=progress_callback
)

print(f"\nProcessing Summary:")
print(f"  Total: {results['total_transactions']}")
print(f"  Successful: {results['successful']}")
print(f"  Failed: {results['failed']}")
print(f"  Throughput: {results['throughput']:.0f} transactions/sec")
print(f"  Duration: {results['total_time']:.2f} seconds")
```

## Advanced Usage

### Custom Batch Processing

```python
from kosha_client import BatchProcessor

processor = BatchProcessor(
    api_url="http://localhost:8000",
    batch_size=2000,
    max_retries=5,
    timeout=120,
    progress_callback=lambda curr, total: print(f"{curr}/{total}")
)

results = processor.process_all(transactions, validate_audit_hash=True)
```

### Audit Hash Validation

```python
from kosha_client import AuditHashValidator

# Validate individual result
is_valid = AuditHashValidator.validate_result(api_result, original_transaction)

# Compute audit hash manually
audit_hash = AuditHashValidator.compute_audit_hash(transaction_data)
```

## API Reference

### KoshaClient

Main client class for API interactions.

**Constructor Parameters:**
- `api_url` (str): Base URL of the Kosha API (default: "http://127.0.0.1:8000")
- `batch_size` (int): Default batch size for bulk operations (default: 1000)
- `max_retries` (int): Maximum number of retry attempts (default: 3)
- `timeout` (int): Request timeout in seconds (default: 60)

**Methods:**
- `health_check()`: Check API health status
- `reconcile_transaction(transaction)`: Process a single transaction
- `reconcile_batch(transactions, validate_audit_hash, progress_callback)`: Process multiple transactions
- `load_transactions_from_csv(file_path, limit)`: Load transactions from CSV file

### BatchProcessor

Low-level batch processing with fine-grained control.

**Constructor Parameters:**
- `api_url` (str): Base URL of the Kosha API
- `batch_size` (int): Number of transactions per batch (max 5000)
- `max_retries` (int): Maximum number of retry attempts
- `timeout` (int): Request timeout in seconds
- `progress_callback` (callable): Optional callback function(current, total)

**Methods:**
- `process_batch(transactions, batch_id)`: Process a single batch
- `process_all(transactions, validate_audit_hash)`: Process all transactions in batches

### AuditHashValidator

Cryptographic validation utilities.

**Static Methods:**
- `compute_audit_hash(data)`: Compute SHA-256 audit hash
- `validate_result(result, original_transaction)`: Validate audit hash integrity

## Examples

See the `examples/` directory for complete usage examples:
- `basic_usage.py`: Simple single transaction processing
- `batch_processing.py`: Large-scale batch processing
- `csv_import.py`: Load and process transactions from CSV
- `audit_validation.py`: Audit hash validation examples

## Error Handling

```python
from requests.exceptions import RequestException

try:
    result = client.reconcile_transaction(transaction)
except RequestException as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
```

## Performance Considerations

- **Batch Size**: Use larger batches (2000-5000) for maximum throughput
- **Retry Logic**: Adjust `max_retries` based on network reliability
- **Timeout**: Increase timeout for large batches: `timeout = batch_size * 0.05`
- **Audit Validation**: Disable for production if not required (adds ~10% overhead)

## Testing

```bash
cd client_sdk/python
pytest tests/ -v
```

## License

MIT License - See LICENSE file for details
