import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  AuthResponse,
  User,
  FileUploadResponse,
  ConversionResult,
  AnalyticsData,
  QualityCheckResult,
  BulkProcessResult,
  ExportOptions,
  JobStatus,
  CacheStats,
} from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

class ApiClient {
  private client: AxiosInstance;
  private apiKey: string | null = null;
  private userId: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add interceptor to include API key in requests
    this.client.interceptors.request.use(
      (config) => {
        if (this.apiKey) {
          config.headers.Authorization = `Bearer ${this.apiKey}`;
        }
        return config;
      },
      (error) => Promise.reject(error),
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.logout();
        }
        return Promise.reject(error);
      },
    );
  }

  // =========================
  // Authentication Methods
  // =========================

  async register(username: string, email: string, password: string): Promise<AuthResponse> {
    try {
      const response = await this.client.post('/auth/register', {
        username,
        email,
        password,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async login(username: string, password: string): Promise<AuthResponse> {
    try {
      const response = await this.client.post('/auth/login', {
        username,
        password,
      });
      
      const data = response.data;
      if (data.success && data.api_key) {
        this.apiKey = data.api_key;
        this.userId = data.user_id;
        
        // Store in AsyncStorage
        await AsyncStorage.multiSet([
          ['userToken', data.api_key],
          ['userId', data.user_id],
          ['username', data.username],
          ['userEmail', data.email || ''],
        ]);
      }
      
      return data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout(): Promise<void> {
    try {
      if (this.apiKey) {
        await this.client.post('/auth/logout');
      }
    } catch (error) {
      console.warn('Logout request failed:', error);
    } finally {
      this.apiKey = null;
      this.userId = null;
      await AsyncStorage.multiRemove([
        'userToken',
        'userId',
        'username',
        'userEmail',
      ]);
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const response = await this.client.get('/auth/me');
      return response.data.user;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async resetApiKey(): Promise<string> {
    try {
      const response = await this.client.post('/auth/reset-api-key');
      if (response.data.success) {
        this.apiKey = response.data.api_key;
        await AsyncStorage.setItem('userToken', response.data.api_key);
        return response.data.api_key;
      }
      throw new Error('Failed to reset API key');
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async restoreSession(): Promise<boolean> {
    try {
      const token = await AsyncStorage.getItem('userToken');
      const userId = await AsyncStorage.getItem('userId');
      
      if (token && userId) {
        this.apiKey = token;
        this.userId = userId;
        
        // Verify token is still valid
        try {
          await this.getCurrentUser();
          return true;
        } catch (error) {
          await this.logout();
          return false;
        }
      }
      return false;
    } catch (error) {
      console.error('Failed to restore session:', error);
      return false;
    }
  }

  // =========================
  // File Operations
  // =========================

  async uploadFile(filepath: string, filename: string): Promise<FileUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: filepath,
        type: this.getMimeType(filename),
        name: filename,
      } as any);

      const response = await this.client.post('/uploads', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async downloadFile(fileId: string, filename: string): Promise<any> {
    try {
      const response = await this.client.get(`/uploads/${fileId}`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // =========================
  // Core Processing Features
  // =========================

  async removeDuplicates(fileId: string): Promise<ConversionResult> {
    try {
      const response = await this.client.post('/pdf/remove-duplicates', {
        file_id: fileId,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async validateData(fileId: string, rules?: Record<string, any>): Promise<QualityCheckResult> {
    try {
      const response = await this.client.post('/features/quality-check', {
        file_id: fileId,
        rules,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async exportToFormat(fileId: string, options: ExportOptions): Promise<ConversionResult> {
    try {
      const response = await this.client.post(`/features/export/${options.format}`, {
        file_id: fileId,
        ...options,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async generateReport(fileId: string, reportType?: string): Promise<ConversionResult> {
    try {
      const response = await this.client.post('/features/export/html', {
        file_id: fileId,
        report_type: reportType,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // =========================
  // Advanced Features
  // =========================

  async checkQuality(fileId: string): Promise<QualityCheckResult> {
    try {
      const response = await this.client.post('/features/quality-check', {
        file_id: fileId,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async bulkProcess(fileIds: string[], operation: string): Promise<BulkProcessResult> {
    try {
      const response = await this.client.post('/features/bulk-process', {
        file_ids: fileIds,
        operation,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async estimateProcessingTime(fileId: string, operation: string): Promise<any> {
    try {
      const response = await this.client.post('/features/performance/estimate', {
        file_id: fileId,
        operation,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // =========================
  // Job Management
  // =========================

  async scheduleJob(operation: string, parameters: Record<string, any>): Promise<any> {
    try {
      const response = await this.client.post('/features/jobs/schedule', {
        operation,
        parameters,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getJobStatus(jobId: string): Promise<JobStatus> {
    try {
      const response = await this.client.get(`/features/jobs/${jobId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // =========================
  // Analytics
  // =========================

  async getAnalytics(): Promise<AnalyticsData> {
    try {
      const response = await this.client.get('/image/analytics');
      return response.data.analytics || response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getCacheStats(): Promise<CacheStats> {
    try {
      const response = await this.client.get('/features/cache/stats');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async clearCache(): Promise<any> {
    try {
      const response = await this.client.post('/features/cache/clear');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // =========================
  // Utility Methods
  // =========================

  private getMimeType(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase();
    const mimeTypes: Record<string, string> = {
      pdf: 'application/pdf',
      csv: 'text/csv',
      xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      xls: 'application/vnd.ms-excel',
      json: 'application/json',
      xml: 'application/xml',
      txt: 'text/plain',
      jpg: 'image/jpeg',
      jpeg: 'image/jpeg',
      png: 'image/png',
      gif: 'image/gif',
    };
    return mimeTypes[ext || ''] || 'application/octet-stream';
  }

  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || error.message;
      return new Error(message);
    }
    return error instanceof Error ? error : new Error('Unknown error occurred');
  }

  isAuthenticated(): boolean {
    return !!this.apiKey;
  }

  getApiKey(): string | null {
    return this.apiKey;
  }

  setApiKey(key: string): void {
    this.apiKey = key;
  }
}

export default new ApiClient();
