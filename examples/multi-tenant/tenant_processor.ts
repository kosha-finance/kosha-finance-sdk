/**
 * Multi-Tenant Processing Example
 *
 * Demonstrates processing transactions for multiple tenants in parallel
 * with proper isolation and reporting.
 */

import { KoshaClient } from '@kosha-finance/client';
import * as fs from 'fs';
import * as path from 'path';
import * as csv from 'csv-parser';

interface Transaction {
  amount: number;
  currency: string;
  transaction_date: string;
  description: string;
  reference_id: string;
}

interface TenantConfig {
  id: string;
  name: string;
  apiKey: string;
  dataPath: string;
}

interface ProcessingReport {
  tenant_id: string;
  tenant_name: string;
  start_time: Date;
  end_time: Date;
  duration_seconds: number;
  total_processed: number;
  matched: number;
  unmatched: number;
  match_rate: number;
  by_match_type: Record<string, number>;
  avg_confidence: number;
  errors: number;
}

class TenantProcessor {
  private client: KoshaClient;
  private batchSize: number;

  constructor(apiKey: string, batchSize: number = 1000) {
    this.client = new KoshaClient({
      apiKey,
      baseUrl: process.env.KOSHA_API_URL || 'https://api.kosha.finance',
      timeout: 30000
    });
    this.batchSize = batchSize;
  }

  /**
   * Load transactions from CSV file
   */
  async loadTransactionsFromCSV(csvPath: string): Promise<Transaction[]> {
    return new Promise((resolve, reject) => {
      const transactions: Transaction[] = [];

      fs.createReadStream(csvPath)
        .pipe(csv())
        .on('data', (row) => {
          transactions.push({
            amount: parseFloat(row.amount),
            currency: row.currency,
            transaction_date: row.transaction_date,
            description: row.description,
            reference_id: row.reference_id
          });
        })
        .on('end', () => resolve(transactions))
        .on('error', reject);
    });
  }

  /**
   * Process transactions with progress tracking
   */
  async processTransactions(
    transactions: Transaction[],
    onProgress?: (current: number, total: number) => void
  ): Promise<any[]> {
    const results: any[] = [];
    const total = transactions.length;

    for (let i = 0; i < total; i += this.batchSize) {
      const batch = transactions.slice(i, Math.min(i + this.batchSize, total));

      try {
        const batchResults = await this.client.batchReconcile(batch);
        results.push(...batchResults);

        if (onProgress) {
          onProgress(Math.min(i + this.batchSize, total), total);
        }
      } catch (error) {
        console.error(`Batch processing error at index ${i}:`, error);
        // Add error placeholders for failed batch
        results.push(...batch.map(() => ({ error: true })));
      }
    }

    return results;
  }

  /**
   * Generate processing report
   */
  generateReport(
    tenantId: string,
    tenantName: string,
    startTime: Date,
    results: any[]
  ): ProcessingReport {
    const endTime = new Date();
    const durationSeconds = (endTime.getTime() - startTime.getTime()) / 1000;

    const matched = results.filter(r => r.is_match && !r.error).length;
    const unmatched = results.filter(r => !r.is_match && !r.error).length;
    const errors = results.filter(r => r.error).length;
    const total = results.length;

    // Count by match type
    const byMatchType: Record<string, number> = {};
    results.forEach(r => {
      if (r.is_match && r.match_type) {
        byMatchType[r.match_type] = (byMatchType[r.match_type] || 0) + 1;
      }
    });

    // Calculate average confidence
    const confidences = results
      .filter(r => r.is_match && r.confidence_score)
      .map(r => parseFloat(r.confidence_score));
    const avgConfidence = confidences.length > 0
      ? confidences.reduce((a, b) => a + b, 0) / confidences.length
      : 0;

    return {
      tenant_id: tenantId,
      tenant_name: tenantName,
      start_time: startTime,
      end_time: endTime,
      duration_seconds: durationSeconds,
      total_processed: total,
      matched,
      unmatched,
      match_rate: total > 0 ? (matched / total) * 100 : 0,
      by_match_type: byMatchType,
      avg_confidence: avgConfidence,
      errors
    };
  }
}

/**
 * Process transactions for a single tenant
 */
async function processTenant(
  config: TenantConfig
): Promise<ProcessingReport> {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`Processing tenant: ${config.name} (${config.id})`);
  console.log('='.repeat(60));

  const processor = new TenantProcessor(config.apiKey);
  const startTime = new Date();

  try {
    // Load transactions
    console.log(`Loading transactions from ${config.dataPath}...`);
    const transactions = await processor.loadTransactionsFromCSV(config.dataPath);
    console.log(`Loaded ${transactions.length} transactions`);

    // Process with progress
    console.log('Processing...');
    const results = await processor.processTransactions(
      transactions,
      (current, total) => {
        const percent = ((current / total) * 100).toFixed(1);
        process.stdout.write(`\rProgress: ${current}/${total} (${percent}%)`);
      }
    );
    console.log(); // New line after progress

    // Generate report
    const report = processor.generateReport(
      config.id,
      config.name,
      startTime,
      results
    );

    // Save report
    const reportPath = `report_${config.id}_${Date.now()}.json`;
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`Report saved: ${reportPath}`);

    // Print summary
    console.log(`\nSummary:`);
    console.log(`  Processed:   ${report.total_processed}`);
    console.log(`  Matched:     ${report.matched} (${report.match_rate.toFixed(1)}%)`);
    console.log(`  Unmatched:   ${report.unmatched}`);
    console.log(`  Errors:      ${report.errors}`);
    console.log(`  Duration:    ${report.duration_seconds.toFixed(1)}s`);
    console.log(`  Confidence:  ${(report.avg_confidence * 100).toFixed(1)}%`);

    return report;
  } catch (error) {
    console.error(`Error processing tenant ${config.name}:`, error);
    throw error;
  }
}

/**
 * Process multiple tenants in parallel
 */
async function processMultipleTenants(configs: TenantConfig[]) {
  console.log(`\nProcessing ${configs.length} tenants in parallel...\n`);

  const startTime = Date.now();

  try {
    const reports = await Promise.all(
      configs.map(config => processTenant(config))
    );

    const duration = (Date.now() - startTime) / 1000;

    // Print overall summary
    console.log(`\n${'='.repeat(60)}`);
    console.log('OVERALL SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total tenants:     ${reports.length}`);
    console.log(`Total duration:    ${duration.toFixed(1)}s`);
    console.log();

    reports.forEach(report => {
      console.log(`${report.tenant_name}:`);
      console.log(`  ${report.matched}/${report.total_processed} matched (${report.match_rate.toFixed(1)}%)`);
    });

    // Save combined report
    const combinedReportPath = `combined_report_${Date.now()}.json`;
    fs.writeFileSync(
      combinedReportPath,
      JSON.stringify({ reports, total_duration: duration }, null, 2)
    );
    console.log(`\nCombined report: ${combinedReportPath}`);

  } catch (error) {
    console.error('Error processing tenants:', error);
    process.exit(1);
  }
}

// Example usage
const tenantConfigs: TenantConfig[] = [
  {
    id: 'tenant-001',
    name: 'Acme Corp',
    apiKey: process.env.TENANT_001_API_KEY || 'key-001',
    dataPath: './data/tenant-001-transactions.csv'
  },
  {
    id: 'tenant-002',
    name: 'TechStart Inc',
    apiKey: process.env.TENANT_002_API_KEY || 'key-002',
    dataPath: './data/tenant-002-transactions.csv'
  }
];

// Run if called directly
if (require.main === module) {
  processMultipleTenants(tenantConfigs)
    .then(() => {
      console.log('\nDone!');
      process.exit(0);
    })
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

export { TenantProcessor, processTenant, processMultipleTenants };
