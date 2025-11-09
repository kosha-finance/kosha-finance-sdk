# Kosha Finance SDK

Official SDKs and documentation for the Kosha Finance Reconciliation API.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)

## About Kosha Finance

Kosha Finance provides intelligent transaction reconciliation and matching services powered by advanced ML algorithms. Our API helps financial institutions, fintech companies, and enterprises automate their reconciliation workflows.

**Website**: [http://kosha.finance](http://kosha.finance)
**LinkedIn**: [https://www.linkedin.com/company/kosha-finance/](https://www.linkedin.com/company/kosha-finance/)

---

## 📦 Installation

### Python

```bash
pip install kosha-finance-client
```

### TypeScript/JavaScript

```bash
npm install @kosha-finance/client
```

---

## 🚀 Quick Start

### Python

```python
from kosha_client import KoshaClient
import os

# Initialize client
client = KoshaClient(
    api_key=os.getenv("KOSHA_API_KEY"),
    base_url="https://api.kosha.finance"
)

# Health check
health = client.health_check()
print(f"API Status: {health['status']}")

# Reconcile a single transaction
transaction = {
    "amount": 100.50,
    "currency": "USD",
    "transaction_date": "2025-01-15",
    "description": "Payment to vendor",
    "reference_id": "INV-001"
}

result = client.reconcile_transaction(transaction)
print(f"Match found: {result['is_match']}")
if result['is_match']:
    print(f"Match Type: {result['match_type']}")
    print(f"Confidence: {result['confidence_score']}")
```

### TypeScript

```typescript
import { KoshaClient } from '@kosha-finance/client';

// Initialize client
const client = new KoshaClient({
  apiKey: process.env.KOSHA_API_KEY || 'your_api_key',
  baseUrl: 'https://api.kosha.finance',
  timeout: 30000 // 30 second timeout
});

// Health check
const health = await client.healthCheck();
console.log(`API Status: ${health.status}`);

// Reconcile a single transaction
const transaction = {
  amount: 100.50,
  currency: 'USD',
  transaction_date: '2025-01-15',
  description: 'Payment to vendor',
  reference_id: 'INV-001'
};

const result = await client.reconcileTransaction(transaction);
console.log(`Match found: ${result.is_match}`);
if (result.is_match) {
  console.log(`Match Type: ${result.match_type}`);
  console.log(`Confidence: ${result.confidence_score}`);
}
```

---

## 📚 Documentation

- **[Getting Started Guide](docs/getting-started.md)** - First steps with the API
- **[Authentication](docs/authentication.md)** - JWT authentication flow
- **[API Reference](docs/api-reference.md)** - Complete endpoint documentation
- **[Rate Limiting](docs/rate-limiting.md)** - Understanding rate limits
- **[Error Handling](docs/error-handling.md)** - Error codes and handling strategies
- **[OpenAPI Schema](openapi.json)** - Machine-readable API specification

---

## 💻 SDK Documentation

### Python SDK

- **[Python SDK Documentation](sdks/python/README.md)**
- **[Python Examples](sdks/python/examples/)**
  - [Basic Usage](sdks/python/examples/basic_usage.py)
  - [Batch Processing](sdks/python/examples/batch_processing.py)
  - [CSV Import](sdks/python/examples/csv_import.py)
  - [Audit Validation](sdks/python/examples/audit_validation.py)

### TypeScript SDK

- **[TypeScript SDK Documentation](sdks/typescript/README.md)**
- **[TypeScript Examples](examples/)**
  - [Getting Started](examples/getting-started/)
  - [Batch Processing](examples/batch-processing/)
  - [Advanced Usage](examples/advanced/)

---

## 🔧 Features

- ✅ **Multi-stage Matching**: Exact, Fuzzy, ML, and LLM-based matching algorithms
- ✅ **Batch Processing**: Process up to 5,000 transactions per batch
- ✅ **Retry Logic**: Built-in exponential backoff for resilient operations
- ✅ **Audit Validation**: Cryptographic verification of reconciliation results
- ✅ **Type Safety**: Full TypeScript types and Python type hints
- ✅ **Progress Tracking**: Real-time progress callbacks for batch operations
- ✅ **Error Handling**: Comprehensive error handling with detailed messages

---

## 🌐 API Endpoints

Base URL: `https://api.kosha.finance/api/v1`

### Authentication
- `POST /auth/register` - Register new account
- `POST /auth/login` - Login and get access token
- `POST /auth/refresh` - Refresh access token

### Transactions
- `POST /transactions/reconcile` - Reconcile single transaction
- `POST /transactions/batch` - Batch reconciliation
- `GET /transactions/stats` - Get matching statistics

### Match Sessions
- `GET /transactions/match-sessions` - List match sessions
- `GET /transactions/match-sessions/{id}` - Get session details
- `GET /transactions/match-sessions/{id}/matches` - Get matches for session

See [OpenAPI Schema](openapi.json) for complete API specification.

---

## 🔑 Authentication

The Kosha Finance API uses JWT (JSON Web Token) authentication:

1. Register or login to get an access token
2. Include the token in the `Authorization` header:
   ```
   Authorization: Bearer your_access_token
   ```

Tokens expire after 15 minutes. Use the refresh token to get a new access token.

See [Authentication Documentation](docs/authentication.md) for details.

---

## 📊 Rate Limiting

| Endpoint Type | Rate Limit |
|--------------|------------|
| Authentication | 10 requests/minute |
| Read Operations | 100 requests/minute |
| Write Operations | 30 requests/minute |
| Admin Endpoints | 200 requests/minute |

Rate limit headers are included in all responses:
- `X-RateLimit-Limit` - Your rate limit
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Reset time (Unix timestamp)

---

## 🛠️ Development

### Python SDK Development

```bash
cd sdks/python
pip install -e ".[dev]"
pytest
```

### TypeScript SDK Development

```bash
cd sdks/typescript
npm install
npm run build
npm test
```

---

## 📝 Examples

### Batch Processing (Python)

```python
from kosha_client import KoshaClient, BatchProcessor

client = KoshaClient(api_key="your_api_key")
processor = BatchProcessor(client)

# Load transactions from CSV
transactions = client.load_transactions_from_csv("transactions.csv")

# Process with progress tracking
def on_progress(current, total):
    print(f"Progress: {current}/{total}")

results = processor.process_all(
    transactions,
    progress_callback=on_progress,
    validate_audit_hash=True
)

print(f"Processed {len(results)} transactions")
```

### Error Handling (TypeScript)

```typescript
import { KoshaClient, KoshaError } from '@kosha-finance/client';

const client = new KoshaClient({ apiKey: 'your_api_key' });

try {
  const result = await client.reconcileTransaction(transaction);
  console.log('Success:', result);
} catch (error) {
  if (error instanceof KoshaError) {
    console.error(`API Error: ${error.message}`);
    console.error(`Status: ${error.statusCode}`);
    console.error(`Details:`, error.details);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

---

## 🎯 Real-World Examples

### Complete Reconciliation Flow (Python)

```python
from kosha_client import KoshaClient, BatchProcessor
import pandas as pd

# Initialize
client = KoshaClient(api_key=os.getenv("KOSHA_API_KEY"))

# 1. Authenticate
auth_response = client.login(
    username="user@company.com",
    password="secure_password"
)
print(f"Authenticated: {auth_response['access_token'][:20]}...")

# 2. Load transactions from CSV
df = pd.read_csv("bank_transactions.csv")
transactions = df.to_dict('records')

# 3. Batch process with progress tracking
processor = BatchProcessor(client, batch_size=1000)

def progress_callback(current, total):
    percentage = (current / total) * 100
    print(f"\rProcessing: {current}/{total} ({percentage:.1f}%)", end="")

results = processor.process_all(
    transactions,
    progress_callback=progress_callback,
    validate_audit_hash=True
)

# 4. Analyze results
matched = sum(1 for r in results if r['is_match'])
unmatched = len(results) - matched
print(f"\n\nMatched: {matched} | Unmatched: {unmatched}")

# 5. Get detailed statistics
stats = client.get_statistics()
print(f"\nMatches by type:")
for match_type, count in stats['matches_by_type'].items():
    print(f"  {match_type}: {count}")

# 6. Export unmatched for review
unmatched_df = pd.DataFrame([
    r for r in results if not r['is_match']
])
unmatched_df.to_csv("unmatched_transactions.csv", index=False)
```

### Multi-Tenant Processing (TypeScript)

```typescript
import { KoshaClient } from '@kosha-finance/client';
import * as fs from 'fs';
import * as csv from 'csv-parser';

interface Transaction {
  amount: number;
  currency: string;
  transaction_date: string;
  description: string;
  reference_id: string;
}

async function reconcileForTenant(
  tenantId: string,
  apiKey: string,
  csvPath: string
) {
  const client = new KoshaClient({
    apiKey,
    baseUrl: 'https://api.kosha.finance'
  });

  // Load transactions from CSV
  const transactions: Transaction[] = [];
  await new Promise((resolve, reject) => {
    fs.createReadStream(csvPath)
      .pipe(csv())
      .on('data', (row) => transactions.push(row))
      .on('end', resolve)
      .on('error', reject);
  });

  console.log(`Processing ${transactions.length} transactions for ${tenantId}`);

  // Process in batches
  const batchSize = 1000;
  const results = [];

  for (let i = 0; i < transactions.length; i += batchSize) {
    const batch = transactions.slice(i, i + batchSize);
    const batchResults = await client.batchReconcile(batch);
    results.push(...batchResults);

    const progress = Math.min(i + batchSize, transactions.length);
    console.log(`Progress: ${progress}/${transactions.length}`);
  }

  // Generate report
  const report = {
    tenant_id: tenantId,
    total_processed: results.length,
    matched: results.filter(r => r.is_match).length,
    unmatched: results.filter(r => !r.is_match).length,
    by_match_type: results.reduce((acc, r) => {
      if (r.match_type) {
        acc[r.match_type] = (acc[r.match_type] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>)
  };

  // Save report
  fs.writeFileSync(
    `report_${tenantId}.json`,
    JSON.stringify(report, null, 2)
  );

  return report;
}

// Process multiple tenants
const tenants = [
  { id: 'tenant-a', apiKey: 'key-a', csvPath: 'tenant-a.csv' },
  { id: 'tenant-b', apiKey: 'key-b', csvPath: 'tenant-b.csv' },
];

Promise.all(
  tenants.map(t => reconcileForTenant(t.id, t.apiKey, t.csvPath))
).then(reports => {
  console.log('\n=== Summary ===');
  reports.forEach(r => {
    console.log(`${r.tenant_id}: ${r.matched}/${r.total_processed} matched`);
  });
});
```

### Webhook Integration Example (Python)

```python
from flask import Flask, request, jsonify
from kosha_client import KoshaClient
import os

app = Flask(__name__)
client = KoshaClient(api_key=os.getenv("KOSHA_API_KEY"))

@app.route('/webhook/transaction', methods=['POST'])
def process_transaction():
    """
    Webhook endpoint that receives transactions from your
    payment processor and reconciles them in real-time
    """
    try:
        data = request.json

        # Transform payment processor data to Kosha format
        transaction = {
            "amount": data["amount"],
            "currency": data["currency"],
            "transaction_date": data["created_at"],
            "description": data["description"],
            "reference_id": data["payment_id"]
        }

        # Reconcile immediately
        result = client.reconcile_transaction(transaction)

        if result['is_match']:
            # Update your database with match info
            update_payment_status(
                payment_id=data["payment_id"],
                matched=True,
                match_type=result['match_type'],
                confidence=result['confidence_score']
            )

            return jsonify({
                "status": "matched",
                "match_type": result['match_type'],
                "confidence": result['confidence_score']
            }), 200
        else:
            # Flag for manual review
            flag_for_review(data["payment_id"])

            return jsonify({
                "status": "requires_review"
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
```

### Advanced Error Handling & Retry Logic (TypeScript)

```typescript
import { KoshaClient, KoshaError, RateLimitError } from '@kosha-finance/client';

class ResilientReconciler {
  private client: KoshaClient;
  private maxRetries = 3;
  private retryDelayMs = 1000;

  constructor(apiKey: string) {
    this.client = new KoshaClient({
      apiKey,
      baseUrl: 'https://api.kosha.finance',
      timeout: 30000
    });
  }

  async reconcileWithRetry(
    transaction: any,
    retryCount = 0
  ): Promise<any> {
    try {
      return await this.client.reconcileTransaction(transaction);
    } catch (error) {
      if (error instanceof RateLimitError) {
        // Wait for rate limit reset
        const resetTime = error.resetTime;
        const waitMs = resetTime - Date.now();
        console.log(`Rate limited. Waiting ${waitMs}ms...`);
        await this.sleep(waitMs);
        return this.reconcileWithRetry(transaction, retryCount);
      }

      if (error instanceof KoshaError) {
        // Handle specific error codes
        switch (error.statusCode) {
          case 401:
            console.error('Authentication failed. Check API key.');
            throw error;
          case 400:
            console.error('Invalid transaction data:', error.details);
            throw error;
          case 500:
          case 502:
          case 503:
            // Server error - retry with exponential backoff
            if (retryCount < this.maxRetries) {
              const delay = this.retryDelayMs * Math.pow(2, retryCount);
              console.log(`Server error. Retrying in ${delay}ms...`);
              await this.sleep(delay);
              return this.reconcileWithRetry(transaction, retryCount + 1);
            }
            throw error;
          default:
            throw error;
        }
      }

      // Unknown error
      throw error;
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Usage
const reconciler = new ResilientReconciler(process.env.KOSHA_API_KEY!);

const transactions = [/* ... */];
const results = [];

for (const txn of transactions) {
  try {
    const result = await reconciler.reconcileWithRetry(txn);
    results.push({ success: true, data: result });
  } catch (error) {
    results.push({ success: false, error: error.message });
  }
}
```

---

## 🤝 Support

- **Email**: opensource@kosha.finance
- **Issues**: [GitHub Issues](https://github.com/kosha-finance/kosha-finance-sdk/issues)
- **LinkedIn**: [Kosha Finance](https://www.linkedin.com/company/kosha-finance/)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Website**: [http://kosha.finance](http://kosha.finance)
- **API Documentation**: [https://kosha-finance.github.io/kosha-finance-sdk/docs/](https://kosha-finance.github.io/kosha-finance-sdk/docs/)
- **LinkedIn**: [https://www.linkedin.com/company/kosha-finance/](https://www.linkedin.com/company/kosha-finance/)
- **GitHub**: [https://github.com/kosha-finance](https://github.com/kosha-finance)

---

**Built with ❤️ by the Kosha Finance Dev Team**
