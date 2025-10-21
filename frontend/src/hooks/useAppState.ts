import { useState, useCallback } from 'react';
import { AppState, UploadedFile, ProcessedChunk, ChatMessage } from '../types';

// Initial app state
const initialState: AppState = {
  currentPage: 'upload',
  uploadedFiles: [],
  processedChunks: [],
  isUploading: false,
  isProcessing: false,
  isChatting: false,
  chatHistory: [],
  error: null
};

export function useAppState() {
  const [appState, setAppState] = useState<AppState>(initialState);

  // Update app state
  const updateAppState = useCallback((updates: Partial<AppState>) => {
    setAppState(prevState => ({
      ...prevState,
      ...updates
    }));
  }, []);

  // Navigate to page
  const navigateToPage = useCallback((page: string) => {
    updateAppState({ currentPage: page });
  }, [updateAppState]);

  // Add uploaded file
  const addUploadedFile = useCallback((file: UploadedFile) => {
    updateAppState(prevState => ({
      uploadedFiles: [...prevState.uploadedFiles, file]
    }));
  }, [updateAppState]);

  // Remove uploaded file
  const removeUploadedFile = useCallback((fileId: string) => {
    updateAppState(prevState => ({
      uploadedFiles: prevState.uploadedFiles.filter(file => file.file_id !== fileId)
    }));
  }, [updateAppState]);

  // Clear all files
  const clearAllFiles = useCallback(() => {
    updateAppState({ uploadedFiles: [] });
  }, [updateAppState]);

  // Add processed chunks
  const addProcessedChunks = useCallback((chunks: ProcessedChunk[]) => {
    updateAppState(prevState => ({
      processedChunks: [...prevState.processedChunks, ...chunks]
    }));
  }, [updateAppState]);

  // Clear all chunks
  const clearAllChunks = useCallback(() => {
    updateAppState({ processedChunks: [] });
  }, [updateAppState]);

  // Add chat message
  const addChatMessage = useCallback((message: ChatMessage) => {
    updateAppState(prevState => ({
      chatHistory: [...prevState.chatHistory, message]
    }));
  }, [updateAppState]);

  // Clear chat history
  const clearChatHistory = useCallback(() => {
    updateAppState({ chatHistory: [] });
  }, [updateAppState]);

  // Set loading state
  const setLoading = useCallback((loading: { uploading?: boolean; processing?: boolean; chatting?: boolean }) => {
    updateAppState(loading);
  }, [updateAppState]);

  // Set error
  const setError = useCallback((error: string | null) => {
    updateAppState({ error });
  }, [updateAppState]);

  // Clear error
  const clearError = useCallback(() => {
    updateAppState({ error: null });
  }, [updateAppState]);

  // Reset app state
  const resetAppState = useCallback(() => {
    setAppState(initialState);
  }, []);

  // Get file by ID
  const getFileById = useCallback((fileId: string) => {
    return appState.uploadedFiles.find(file => file.file_id === fileId);
  }, [appState.uploadedFiles]);

  // Get chunks by file ID
  const getChunksByFileId = useCallback((fileId: string) => {
    return appState.processedChunks.filter(chunk => 
      chunk.metadata.file_id === fileId
    );
  }, [appState.processedChunks]);

  // Get recent chat messages
  const getRecentChatMessages = useCallback((limit: number = 10) => {
    return appState.chatHistory
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }, [appState.chatHistory]);

  // Check if file is uploaded
  const isFileUploaded = useCallback((filename: string) => {
    return appState.uploadedFiles.some(file => file.filename === filename);
  }, [appState.uploadedFiles]);

  // Get total file size
  const getTotalFileSize = useCallback(() => {
    return appState.uploadedFiles.reduce((total, file) => total + file.size, 0);
  }, [appState.uploadedFiles]);

  // Get file count by type
  const getFileCountByType = useCallback(() => {
    const counts: { [key: string]: number } = {};
    appState.uploadedFiles.forEach(file => {
      const type = file.content_type;
      counts[type] = (counts[type] || 0) + 1;
    });
    return counts;
  }, [appState.uploadedFiles]);

  return {
    appState,
    updateAppState,
    navigateToPage,
    addUploadedFile,
    removeUploadedFile,
    clearAllFiles,
    addProcessedChunks,
    clearAllChunks,
    addChatMessage,
    clearChatHistory,
    setLoading,
    setError,
    clearError,
    resetAppState,
    getFileById,
    getChunksByFileId,
    getRecentChatMessages,
    isFileUploaded,
    getTotalFileSize,
    getFileCountByType
  };
}
