# CSV Import Example

Process and reconcile transactions from CSV files using the Kosha Finance API.

## Features

- Load transactions from CSV
- Batch processing with progress tracking
- Audit hash validation
- Export results to CSV
- Generate summary reports

## Installation

```bash
pip install kosha-finance-client pandas
```

## Usage

Basic usage:
```bash
export KOSHA_API_KEY="your_api_key"
python reconcile_csv.py --input sample_transactions.csv --output results.csv
```

Export unmatched transactions:
```bash
python reconcile_csv.py \
  --input transactions.csv \
  --output results.csv \
  --unmatched-output unmatched.csv
```

Custom batch size:
```bash
python reconcile_csv.py \
  --input large_file.csv \
  --batch-size 5000 \
  --output results.csv
```

## CSV Format

Input CSV should contain these columns:
- `amount` - Transaction amount (numeric)
- `currency` - Currency code (e.g., USD, EUR)
- `transaction_date` - Date in YYYY-MM-DD format
- `description` - Transaction description
- `reference_id` - Unique reference identifier

## Output

The script generates:
1. Results CSV with match status and confidence scores
2. Console summary report with statistics
3. Optional unmatched transactions CSV
