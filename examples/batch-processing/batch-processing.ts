/**
 * Batch processing example for Kosha Finance TypeScript Client SDK.
 *
 * Demonstrates:
 * - Batch reconciliation
 * - Progress tracking
 * - Error handling for large batches
 * - Processing statistics
 */

import { KoshaClient, BatchProcessor } from '@kosha-finance/client';

async function main() {
  console.log('='.repeat(60));
  console.log('Kosha Finance Client SDK - Batch Processing Example');
  console.log('='.repeat(60));

  // Initialize client
  const client = new KoshaClient({
    apiUrl: 'https://api.kosha.finance',
    apiKey: process.env.KOSHA_API_KEY || 'your_api_key_here',
    timeout: 60000
  });

  // Initialize batch processor
  const processor = new BatchProcessor(client);

  // Create sample transactions
  console.log('\n1. Creating sample transactions...');
  const transactions = [];
  for (let i = 0; i < 100; i++) {
    transactions.push({
      amount: Math.round((Math.random() * 10000 + 100) * 100) / 100,
      currency: 'USD',
      transaction_date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
        .toISOString()
        .split('T')[0],
      description: `Sample Transaction ${i + 1}`,
      merchant_name: ['Acme Corp', 'TechSupply Inc', 'Office Depot', 'Amazon'][i % 4],
      transaction_type: i % 2 === 0 ? 'debit' : 'credit',
      category: 'business_expense'
    });
  }
  console.log(`   ✓ Created ${transactions.length} sample transactions`);

  // Process batch with progress tracking
  console.log('\n2. Processing batch...');
  const startTime = Date.now();

  try {
    const results = await processor.processAll(transactions, {
      onProgress: (current, total) => {
        const percent = ((current / total) * 100).toFixed(1);
        process.stdout.write(`\r   Progress: ${current}/${total} (${percent}%)`);
      },
      validateAuditHash: true
    });

    const duration = ((Date.now() - startTime) / 1000).toFixed(2);

    console.log('\n\n3. Processing Statistics:');
    console.log(`   ✓ Total Transactions: ${results.length}`);
    console.log(`   ✓ Processing Time: ${duration}s`);
    console.log(`   ✓ Throughput: ${(results.length / parseFloat(duration)).toFixed(2)} txns/sec`);

    // Calculate match statistics
    const matchStats = results.reduce(
      (stats, result) => {
        if (result.is_match) {
          stats.matched++;
          stats.byType[result.match_type] = (stats.byType[result.match_type] || 0) + 1;
        }
        return stats;
      },
      { matched: 0, byType: {} as Record<string, number> }
    );

    console.log(`   ✓ Matches Found: ${matchStats.matched}/${results.length}`);
    console.log(`   ✓ Match Rate: ${((matchStats.matched / results.length) * 100).toFixed(2)}%`);
    console.log('\n   Match Types:');
    Object.entries(matchStats.byType).forEach(([type, count]) => {
      console.log(`     - ${type}: ${count}`);
    });

  } catch (error) {
    console.error(`\n   ✗ Batch processing failed: ${error}`);
    process.exit(1);
  }

  console.log('\n' + '='.repeat(60));
  console.log('✓ Batch processing example completed successfully');
  console.log('='.repeat(60));
}

// Run the example
main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
