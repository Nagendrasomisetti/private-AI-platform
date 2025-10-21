// API Response Types
export interface HealthResponse {
  status: string;
  version: string;
  uptime: number;
}

export interface ErrorResponse {
  error: string;
  detail: string;
}

export interface UploadResponse {
  status: string;
  message: string;
  file_id: string;
}

export interface DatabaseRequest {
  db_url: string;
}

export interface DatabaseResponse {
  status: string;
  message: string;
}

export interface IngestResponse {
  status: string;
  message: string;
  chunks_processed: number;
}

export interface ChatRequest {
  query: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  metadata: ChatMetadata;
}

export interface Source {
  text: string;
  metadata: SourceMetadata;
  similarity_score: number;
  rank: number;
}

export interface SourceMetadata {
  source_file: string;
  page_number?: number;
  chunk_index?: number;
  file_id?: string;
  chunk_type?: string;
  department?: string;
  confidentiality?: string;
  last_updated?: string;
}

export interface ChatMetadata {
  query: string;
  retrieved_chunks: number;
  processing_time: number;
  model_used: string;
  cached: boolean;
  error?: string;
}

// File Types
export interface UploadedFile {
  file_id: string;
  filename: string;
  file_path: string;
  content_type: string;
  size: number;
  uploaded_at: number;
}

export interface ProcessedChunk {
  chunk_id: string;
  text: string;
  metadata: SourceMetadata;
}

// UI State Types
export interface AppState {
  currentPage: string;
  uploadedFiles: UploadedFile[];
  processedChunks: ProcessedChunk[];
  isUploading: boolean;
  isProcessing: boolean;
  isChatting: boolean;
  chatHistory: ChatMessage[];
  error: string | null;
}

export interface ChatMessage {
  id: string;
  query: string;
  answer: string;
  sources: Source[];
  timestamp: number;
  metadata: ChatMetadata;
}

// Component Props Types
export interface PageProps {
  onNavigate: (page: string) => void;
  appState: AppState;
  updateAppState: (updates: Partial<AppState>) => void;
}

export interface UploadPageProps extends PageProps {
  onFileUpload: (file: File) => Promise<void>;
  onDatabaseConnect: (dbUrl: string) => Promise<void>;
}

export interface IngestionPageProps extends PageProps {
  onStartIngestion: () => Promise<void>;
  onClearData: () => Promise<void>;
}

export interface ChatPageProps extends PageProps {
  onSendMessage: (query: string) => Promise<void>;
}

// Utility Types
export type PageName = 'upload' | 'ingestion' | 'chat';

export type ButtonVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'outline' | 'ghost';

export type ButtonSize = 'sm' | 'md' | 'lg';

export type AlertType = 'success' | 'warning' | 'error' | 'info';

// API Configuration
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
}

// Sample Data Types
export interface SampleData {
  files: UploadedFile[];
  chunks: ProcessedChunk[];
  chatMessages: ChatMessage[];
}
