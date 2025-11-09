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

# Initialize client
client = KoshaClient(
    api_key="your_api_key",
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
    "description": "Payment to vendor"
}

result = client.reconcile_transaction(transaction)
print(f"Match found: {result['is_match']}")
```

### TypeScript

```typescript
import { KoshaClient } from '@kosha-finance/client';

// Initialize client
const client = new KoshaClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.kosha.finance'
});

// Health check
const health = await client.healthCheck();
console.log(`API Status: ${health.status}`);

// Reconcile a single transaction
const transaction = {
  amount: 100.50,
  currency: 'USD',
  transaction_date: '2025-01-15',
  description: 'Payment to vendor'
};

const result = await client.reconcileTransaction(transaction);
console.log(`Match found: ${result.is_match}`);
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
