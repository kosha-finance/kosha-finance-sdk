# Kosha Finance API Examples

Real-world integration examples and demos for the Kosha Finance API.

## Available Examples

### 1. CSV Import (`csv-import/`)

Process and reconcile transactions from CSV files with batch processing and progress tracking.

**Features:**
- Load transactions from CSV
- Batch processing with configurable size
- Real-time progress tracking
- Export results and unmatched transactions
- Generate summary reports

**Quick Start:**
```bash
cd csv-import
pip install kosha-finance-client pandas
export KOSHA_API_KEY="your_api_key"
python reconcile_csv.py --input sample_transactions.csv --output results.csv
```

---

### 2. Webhook Integration (`webhook-integration/`)

Real-time transaction reconciliation via Flask webhook endpoint.

**Features:**
- Webhook endpoint for payment processors
- Single transaction and batch processing
- Health check endpoint
- Error handling and logging
- Test script included

**Quick Start:**
```bash
cd webhook-integration
pip install kosha-finance-client flask
export KOSHA_API_KEY="your_api_key"
python flask_webhook.py

# In another terminal
./test_webhook.sh
```

---

### 3. Multi-Tenant Processing (`multi-tenant/`)

Process transactions for multiple tenants in parallel with proper isolation.

**Features:**
- Parallel tenant processing
- Per-tenant reports and statistics
- Combined summary report
- CSV data loading
- Progress tracking per tenant

**Quick Start:**
```bash
cd multi-tenant
npm install @kosha-finance/client csv-parser
export TENANT_001_API_KEY="key_1"
export TENANT_002_API_KEY="key_2"
npx ts-node tenant_processor.ts
```

---

## Common Requirements

### Python Examples
```bash
pip install kosha-finance-client pandas flask
```

### TypeScript Examples
```bash
npm install @kosha-finance/client csv-parser @types/node
```

## Environment Variables

All examples require API authentication:

```bash
# Single tenant
export KOSHA_API_KEY="your_api_key"

# Multi-tenant
export TENANT_001_API_KEY="tenant_1_key"
export TENANT_002_API_KEY="tenant_2_key"

# Optional: Custom API URL
export KOSHA_API_URL="https://api.kosha.finance"
```

## Example Data Format

Transactions should follow this structure:

```json
{
  "amount": 100.50,
  "currency": "USD",
  "transaction_date": "2025-01-15",
  "description": "Payment to vendor",
  "reference_id": "INV-001"
}
```

## Response Format

Successful matches return:

```json
{
  "is_match": true,
  "match_type": "ml",
  "confidence_score": "0.9500",
  "match_id": "uuid",
  "matched_transaction_id": "uuid"
}
```

## Support

- **Documentation**: [https://kosha-finance.github.io/kosha-finance-sdk/docs/](https://kosha-finance.github.io/kosha-finance-sdk/docs/)
- **Issues**: [GitHub Issues](https://github.com/kosha-finance/kosha-finance-sdk/issues)
- **Email**: opensource@kosha.finance

## License

MIT License - see [../LICENSE](../LICENSE) for details
