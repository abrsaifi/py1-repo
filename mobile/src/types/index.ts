export interface AuthResponse {
  success: boolean;
  user_id?: string;
  username?: string;
  email?: string;
  api_key?: string;
  message?: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  api_key: string;
  created_at: string;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isSignout: boolean;
  signIn: (username: string, password: string) => Promise<void>;
  signUp: (username: string, email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  resetApiKey: () => Promise<string>;
}

export interface FileUploadResponse {
  success: boolean;
  file_id?: string;
  filename?: string;
  size?: number;
  message?: string;
}

export interface ConversionResult {
  success: boolean;
  file_id?: string;
  file_url?: string;
  format?: string;
  size?: number;
  duration?: number;
  message?: string;
}

export interface AnalyticsData {
  total_files: number;
  total_operations: number;
  success_rate: number;
  average_processing_time: number;
  total_storage_used: number;
  files_by_type: Record<string, number>;
  operations_by_type: Record<string, number>;
}

export interface QualityCheckResult {
  success: boolean;
  duplicate_rows?: number;
  missing_values?: number;
  data_quality_score?: number;
  issues?: string[];
  recommendations?: string[];
}

export interface BulkProcessResult {
  success: boolean;
  processed_files?: number;
  failed_files?: number;
  results?: Array<{
    filename: string;
    success: boolean;
    error?: string;
    duration?: number;
  }>;
}

export interface ExportOptions {
  format: 'json' | 'xml' | 'csv' | 'parquet' | 'html';
  include_metadata?: boolean;
  prettify?: boolean;
}

export interface JobStatus {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress?: number;
  result?: any;
  error?: string;
  created_at: string;
  completed_at?: string;
}

export interface CacheStats {
  total_items: number;
  total_size: number;
  hit_rate: number;
  miss_rate: number;
  items: Array<{
    key: string;
    size: number;
    created_at: string;
  }>;
}

export interface WebhookRegistration {
  success: boolean;
  webhook_id?: string;
  event_type?: string;
  url?: string;
  message?: string;
}
