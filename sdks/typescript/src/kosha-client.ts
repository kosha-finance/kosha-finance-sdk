/**
 * Kosha TypeScript/JavaScript Client SDK
 *
 * Production-ready client for the Kosha Reconciliation API with:
 * - Batch processing with automatic chunking
 * - Retry logic with exponential backoff
 * - Audit hash validation
 * - Progress tracking and error handling
 * - TypeScript type safety
 */

import crypto from 'crypto';

/**
 * Transaction input structure
 */
export interface Transaction {
  client_id: string;
  transaction_id: string;
  sequence_id: number;
  event_timestamp: string;
  execution_timestamp: string;
  ledger_a_amount: number;
  ledger_a_fx: number;
  ledger_a_fee: number;
  ledger_b_amount: number;
  ledger_b_fx: number;
  ledger_b_fee: number;
  currency: string;
  vendor_name: string;
  counterparty_name: string;
  source_system_id: string;
  context_data?: Record<string, any>;
}

/**
 * Inference result from API
 */
export interface InferenceResult {
  audit_hash: string;
  exception_flag: boolean;
  reason_code: string;
  confidence: number;
  explainability_features?: Record<string, any>;
}

/**
 * Transaction result with metadata
 */
export interface TransactionResult extends InferenceResult {
  transaction_id: string;
  request_timestamp: string;
  response_timestamp: string;
}

/**
 * Batch processing result
 */
export interface BatchResult {
  batch_id: number;
  total_transactions: number;
  successful: number;
  failed: number;
  results: TransactionResult[];
  duration_seconds: number;
  throughput: number;
}

/**
 * Overall processing summary
 */
export interface ProcessingSummary {
  total_transactions: number;
  successful: number;
  failed: number;
  failed_batches: Array<{ batch_id: number; error: string }>;
  total_time: number;
  throughput: number;
  results: TransactionResult[];
}

/**
 * Client configuration options
 */
export interface KoshaClientConfig {
  apiUrl?: string;
  batchSize?: number;
  maxRetries?: number;
  timeout?: number;
  retryDelay?: number;
}

/**
 * Audit hash validator
 */
export class AuditHashValidator {
  /**
   * Compute SHA-256 audit hash matching server implementation
   */
  static computeAuditHash(data: Record<string, any>): string {
    // Match server: JSON.stringify with sorted keys (deep, deterministic)
    const deepSortObject = (obj: any): any => {
      if (Array.isArray(obj)) {
        return obj.map(deepSortObject);
      } else if (obj !== null && typeof obj === 'object') {
        const sortedKeys = Object.keys(obj).sort();
        const result: any = {};
        for (const key of sortedKeys) {
          result[key] = deepSortObject(obj[key]);
        }
        return result;
      } else {
        return obj;
      }
    };
    const sortedData = deepSortObject(data);
    const serialized = JSON.stringify(sortedData);
    return crypto.createHash('sha256').update(serialized).digest('hex');
  }

  /**
   * Validate that audit hash in result matches original transaction
   */
  static validateResult(
    result: InferenceResult,
    originalTransaction: Transaction
  ): boolean {
    if (!result.audit_hash) {
      return false;
    }

    // Reconstruct the data that should have been hashed
    const expectedData = {
      ...originalTransaction,
      exception_flag: result.exception_flag,
      reason_code: result.reason_code,
      confidence: result.confidence,
    };

    const computedHash = this.computeAuditHash(expectedData);
    return computedHash === result.audit_hash;
  }
}

/**
 * Batch processor with retry logic
 */
export class BatchProcessor {
  private apiUrl: string;
  private batchSize: number;
  private maxRetries: number;
  private timeout: number;
  private retryDelay: number;

  constructor(config: KoshaClientConfig) {
    this.apiUrl = (config.apiUrl || 'http://127.0.0.1:8000').replace(/\/$/, '');
    this.batchSize = Math.min(config.batchSize || 1000, 5000);
    this.maxRetries = config.maxRetries || 3;
    this.timeout = config.timeout || 60000;
    this.retryDelay = config.retryDelay || 1000;
  }

  /**
   * Process a single batch with retry logic
   */
  async processBatch(
    transactions: Transaction[],
    batchId: number = 0
  ): Promise<BatchResult> {
    const startTime = Date.now();
    const requestTimestamp = new Date().toISOString();

    let lastError: Error | null = null;

    // Retry loop
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(
          `${this.apiUrl}/paid-api/v1/reconcile/batch`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(transactions),
            signal: controller.signal,
          }
        );

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(
            `Batch ${batchId} failed with status ${response.status}: ${errorText}`
          );
        }

        const resultsJson = (await response.json()) as InferenceResult[];
        const responseTimestamp = new Date().toISOString();
        const duration = (Date.now() - startTime) / 1000;

        const results: TransactionResult[] = resultsJson.map((result, i) => ({
          ...result,
          transaction_id: transactions[i].transaction_id,
          request_timestamp: requestTimestamp,
          response_timestamp: responseTimestamp,
        }));

        return {
          batch_id: batchId,
          total_transactions: transactions.length,
          successful: results.length,
          failed: 0,
          results,
          duration_seconds: duration,
          throughput: duration > 0 ? transactions.length / duration : 0,
        };
      } catch (error) {
        lastError = error as Error;

        if (attempt < this.maxRetries) {
          // Exponential backoff
          const delay = this.retryDelay * Math.pow(2, attempt);
          await new Promise((resolve) => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError || new Error(`Batch ${batchId} failed after ${this.maxRetries} retries`);
  }

  /**
   * Process all transactions in batches
   */
  async processAll(
    transactions: Transaction[],
    options: {
      validateAuditHash?: boolean;
      onProgress?: (current: number, total: number) => void;
    } = {}
  ): Promise<ProcessingSummary> {
    const { validateAuditHash = false, onProgress } = options;
    const total = transactions.length;
    const allResults: TransactionResult[] = [];
    const failedBatches: Array<{ batch_id: number; error: string }> = [];
    const startTime = Date.now();

    // Process in batches
    for (let i = 0; i < total; i += this.batchSize) {
      const batchId = Math.floor(i / this.batchSize) + 1;
      const batch = transactions.slice(i, i + this.batchSize);

      try {
        const batchResult = await this.processBatch(batch, batchId);
        allResults.push(...batchResult.results);

        // Optional audit hash validation
        if (validateAuditHash) {
          const invalidHashes: string[] = [];
          batchResult.results.forEach((result, j) => {
            const original = batch[j];
            if (!AuditHashValidator.validateResult(result, original)) {
              invalidHashes.push(result.transaction_id);
            }
          });

          if (invalidHashes.length > 0) {
            console.warn(
              `Warning: Batch ${batchId} has ${invalidHashes.length} invalid audit hashes`
            );
          }
        }

        // Progress callback
        if (onProgress) {
          onProgress(i + batch.length, total);
        }
      } catch (error) {
        failedBatches.push({
          batch_id: batchId,
          error: (error as Error).message,
        });
        console.error(`Error processing batch ${batchId}:`, error);
      }
    }

    const totalTime = (Date.now() - startTime) / 1000;

    return {
      total_transactions: total,
      successful: allResults.length,
      failed: total - allResults.length,
      failed_batches: failedBatches,
      total_time: totalTime,
      throughput: total / totalTime,
      results: allResults,
    };
  }
}

/**
 * High-level Kosha API client
 */
export class KoshaClient {
  private apiUrl: string;
  private batchSize: number;
  private maxRetries: number;
  private timeout: number;
  private retryDelay: number;

  /**
   * Initialize Kosha client
   */
  constructor(config: KoshaClientConfig = {}) {
    this.apiUrl = (config.apiUrl || 'http://127.0.0.1:8000').replace(/\/$/, '');
    this.batchSize = config.batchSize || 1000;
    this.maxRetries = config.maxRetries || 3;
    this.timeout = config.timeout || 60000;
    this.retryDelay = config.retryDelay || 1000;
  }

  /**
   * Check API health status
   */
  async healthCheck(): Promise<{ status: string; model_loaded?: boolean }> {
    const response = await fetch(`${this.apiUrl}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error(`Health check failed with status ${response.status}`);
    }

    return response.json() as Promise<{
      status: string;
      model_loaded?: boolean;
    }>;
  }

  /**
   * Process a single transaction
   */
  async reconcileTransaction(transaction: Transaction): Promise<InferenceResult> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.apiUrl}/paid-api/v1/reconcile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transaction),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error ${response.status}: ${errorText}`);
      }

      return (await response.json()) as InferenceResult;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }

  /**
   * Process multiple transactions in batches
   */
  async reconcileBatch(
    transactions: Transaction[],
    options: {
      validateAuditHash?: boolean;
      onProgress?: (current: number, total: number) => void;
    } = {}
  ): Promise<ProcessingSummary> {
    const processor = new BatchProcessor({
      apiUrl: this.apiUrl,
      batchSize: this.batchSize,
      maxRetries: this.maxRetries,
      timeout: this.timeout,
      retryDelay: this.retryDelay,
    });

    return processor.processAll(transactions, options);
  }
}

// Export for CommonJS compatibility
export default KoshaClient;
