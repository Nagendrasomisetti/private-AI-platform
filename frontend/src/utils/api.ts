import axios, { AxiosResponse } from 'axios';
import {
  HealthResponse,
  UploadResponse,
  DatabaseRequest,
  DatabaseResponse,
  IngestResponse,
  ChatRequest,
  ChatResponse,
  ErrorResponse
} from '../types';

// API Configuration
const API_CONFIG = {
  baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  retries: 3
};

// Create axios instance
const api = axios.create({
  baseURL: API_CONFIG.baseUrl,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API Functions
export const apiService = {
  // Health Check
  async getHealth(): Promise<HealthResponse> {
    const response: AxiosResponse<HealthResponse> = await api.get('/health');
    return response.data;
  },

  // File Upload
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response: AxiosResponse<UploadResponse> = await api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Database Connection
  async connectDatabase(dbUrl: string): Promise<DatabaseResponse> {
    const request: DatabaseRequest = { db_url: dbUrl };
    const response: AxiosResponse<DatabaseResponse> = await api.post('/connect-db/', request);
    return response.data;
  },

  // Data Ingestion
  async startIngestion(): Promise<IngestResponse> {
    const response: AxiosResponse<IngestResponse> = await api.post('/ingest/');
    return response.data;
  },

  // Chat
  async sendChatMessage(query: string): Promise<ChatResponse> {
    const request: ChatRequest = { query };
    const response: AxiosResponse<ChatResponse> = await api.post('/chat/', request);
    return response.data;
  },

  // Get Files
  async getFiles(): Promise<{ files: string[]; count: number }> {
    const response = await api.get('/files/');
    return response.data;
  },

  // Get Chunks
  async getChunks(): Promise<{ chunks: any[]; count: number }> {
    const response = await api.get('/chunks/');
    return response.data;
  }
};

// Error handling utility
export const handleApiError = (error: any): string => {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

// Retry utility
export const withRetry = async <T>(
  fn: () => Promise<T>,
  retries: number = API_CONFIG.retries
): Promise<T> => {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0) {
      console.log(`🔄 Retrying... (${retries} attempts left)`);
      await new Promise(resolve => setTimeout(resolve, 1000));
      return withRetry(fn, retries - 1);
    }
    throw error;
  }
};

// API Status Check
export const checkApiStatus = async (): Promise<boolean> => {
  try {
    await apiService.getHealth();
    return true;
  } catch (error) {
    console.error('❌ API Status Check Failed:', error);
    return false;
  }
};

export default apiService;
