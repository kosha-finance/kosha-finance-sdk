/**
 * Basic usage example for Kosha Finance TypeScript Client SDK.
 *
 * Demonstrates:
 * - Client initialization
 * - Health check
 * - Single transaction processing
 * - Basic error handling
 */

import { KoshaClient } from '@kosha-finance/client';

async function main() {
  console.log('='.repeat(60));
  console.log('Kosha Finance Client SDK - Basic Usage Example');
  console.log('='.repeat(60));

  // Initialize client
  const client = new KoshaClient({
    apiUrl: 'https://api.kosha.finance',
    apiKey: process.env.KOSHA_API_KEY || 'your_api_key_here',
    timeout: 30000
  });

  // 1. Health Check
  console.log('\n1. Checking API health...');
  try {
    const health = await client.healthCheck();
    console.log(`   ✓ API Status: ${health.status}`);
    console.log(`   ✓ Model Loaded: ${health.model_loaded ?? 'unknown'}`);
  } catch (error) {
    console.error(`   ✗ Health check failed: ${error}`);
    console.error('\n   Make sure the API is accessible and your API key is valid');
    process.exit(1);
  }

  // 2. Process a single transaction
  console.log('\n2. Processing single transaction...');
  const transaction = {
    amount: 100.50,
    currency: 'USD',
    transaction_date: new Date().toISOString().split('T')[0],
    description: 'Payment to Acme Corporation',
    merchant_name: 'Acme Corporation',
    transaction_type: 'debit',
    category: 'business_expense'
  };

  try {
    const result = await client.reconcileTransaction(transaction);
    console.log('   ✓ Transaction processed successfully');
    console.log(`   ✓ Match Found: ${result.is_match}`);
    console.log(`   ✓ Match Type: ${result.match_type}`);
    console.log(`   ✓ Confidence: ${(result.confidence * 100).toFixed(2)}%`);
    if (result.match_details) {
      console.log(`   ✓ Match Details:`, JSON.stringify(result.match_details, null, 2));
    }
  } catch (error) {
    console.error(`   ✗ Transaction processing failed: ${error}`);
    process.exit(1);
  }

  console.log('\n' + '='.repeat(60));
  console.log('✓ Basic usage example completed successfully');
  console.log('='.repeat(60));
}

// Run the example
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
