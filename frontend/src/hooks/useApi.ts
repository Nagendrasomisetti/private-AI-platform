import { useState, useCallback } from 'react';
import { apiService, handleApiError } from '../utils/api';
import { UploadedFile, ProcessedChunk, ChatMessage } from '../types';

export function useApi() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generic API call wrapper
  const apiCall = useCallback(async <T>(
    apiFunction: () => Promise<T>,
    loadingState: boolean = true
  ): Promise<T | null> => {
    try {
      if (loadingState) setIsLoading(true);
      setError(null);
      
      const result = await apiFunction();
      return result;
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      console.error('API Error:', errorMessage);
      return null;
    } finally {
      if (loadingState) setIsLoading(false);
    }
  }, []);

  // File upload
  const uploadFile = useCallback(async (file: File): Promise<UploadedFile | null> => {
    const result = await apiCall(async () => {
      const response = await apiService.uploadFile(file);
      
      // Convert response to UploadedFile format
      const uploadedFile: UploadedFile = {
        file_id: response.file_id,
        filename: file.name,
        file_path: '', // Will be set by backend
        content_type: file.type,
        size: file.size,
        uploaded_at: Date.now()
      };
      
      return uploadedFile;
    });
    
    return result;
  }, [apiCall]);

  // Database connection
  const connectDatabase = useCallback(async (dbUrl: string): Promise<boolean> => {
    const result = await apiCall(async () => {
      const response = await apiService.connectDatabase(dbUrl);
      return response.status === 'success';
    });
    
    return result || false;
  }, [apiCall]);

  // Start ingestion
  const startIngestion = useCallback(async (): Promise<ProcessedChunk[] | null> => {
    const result = await apiCall(async () => {
      const response = await apiService.startIngestion();
      
      // Convert response to ProcessedChunk format
      const chunks: ProcessedChunk[] = [];
      for (let i = 0; i < response.chunks_processed; i++) {
        chunks.push({
          chunk_id: `chunk_${Date.now()}_${i}`,
          text: `Mock chunk ${i} from ingested data`,
          metadata: {
            source_file: 'ingested_data',
            chunk_index: i,
            chunk_type: 'ingested'
          }
        });
      }
      
      return chunks;
    });
    
    return result;
  }, [apiCall]);

  // Send chat message
  const sendChatMessage = useCallback(async (query: string): Promise<ChatMessage | null> => {
    const result = await apiCall(async () => {
      const response = await apiService.sendChatMessage(query);
      
      // Convert response to ChatMessage format
      const chatMessage: ChatMessage = {
        id: `msg_${Date.now()}`,
        query: response.metadata.query,
        answer: response.answer,
        sources: response.sources,
        timestamp: Date.now(),
        metadata: response.metadata
      };
      
      return chatMessage;
    });
    
    return result;
  }, [apiCall]);

  // Get files
  const getFiles = useCallback(async (): Promise<string[]> => {
    const result = await apiCall(async () => {
      const response = await apiService.getFiles();
      return response.files;
    });
    
    return result || [];
  }, [apiCall]);

  // Get chunks
  const getChunks = useCallback(async (): Promise<ProcessedChunk[]> => {
    const result = await apiCall(async () => {
      const response = await apiService.getChunks();
      
      // Convert response to ProcessedChunk format
      const chunks: ProcessedChunk[] = response.chunks.map((chunk: any, index: number) => ({
        chunk_id: chunk.chunk_id || `chunk_${index}`,
        text: chunk.text || 'No text available',
        metadata: chunk.metadata || {
          source_file: 'unknown',
          chunk_index: index,
          chunk_type: 'unknown'
        }
      }));
      
      return chunks;
    });
    
    return result || [];
  }, [apiCall]);

  // Health check
  const checkHealth = useCallback(async (): Promise<boolean> => {
    const result = await apiCall(async () => {
      const response = await apiService.getHealth();
      return response.status === 'healthy';
    }, false);
    
    return result || false;
  }, [apiCall]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isLoading,
    error,
    clearError,
    uploadFile,
    connectDatabase,
    startIngestion,
    sendChatMessage,
    getFiles,
    getChunks,
    checkHealth
  };
}
