import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Utility function for combining class names
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format file size
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format timestamp
export function formatTimestamp(timestamp: number): string {
  return new Date(timestamp).toLocaleString();
}

// Format duration
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }
  
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  
  if (minutes < 60) {
    return `${minutes}m ${remainingSeconds.toFixed(1)}s`;
  }
  
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  
  return `${hours}h ${remainingMinutes}m ${remainingSeconds.toFixed(1)}s`;
}

// Truncate text
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

// Generate unique ID
export function generateId(): string {
  return Math.random().toString(36).substr(2, 9);
}

// Validate file type
export function validateFileType(file: File, allowedTypes: string[]): boolean {
  return allowedTypes.includes(file.type);
}

// Validate file size
export function validateFileSize(file: File, maxSizeMB: number): boolean {
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  return file.size <= maxSizeBytes;
}

// Validate database URL
export function validateDatabaseUrl(url: string): boolean {
  const patterns = [
    /^postgresql:\/\/.+/,
    /^mysql:\/\/.+/,
    /^sqlite:\/\/.+/,
    /^mongodb:\/\/.+/
  ];
  
  return patterns.some(pattern => pattern.test(url));
}

// Debounce function
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Throttle function
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// Copy to clipboard
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    return false;
  }
}

// Download file
export function downloadFile(content: string, filename: string, type: string = 'text/plain'): void {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Get file extension
export function getFileExtension(filename: string): string {
  return filename.split('.').pop()?.toLowerCase() || '';
}

// Get file icon
export function getFileIcon(filename: string): string {
  const extension = getFileExtension(filename);
  
  const iconMap: { [key: string]: string } = {
    pdf: '📄',
    docx: '📝',
    doc: '📝',
    csv: '📊',
    xlsx: '📊',
    xls: '📊',
    txt: '📄',
    md: '📝',
    json: '📄',
    xml: '📄',
    html: '🌐',
    css: '🎨',
    js: '⚡',
    ts: '⚡',
    py: '🐍',
    java: '☕',
    cpp: '⚙️',
    c: '⚙️',
    default: '📁'
  };
  
  return iconMap[extension] || iconMap.default;
}

// Format similarity score
export function formatSimilarityScore(score: number): string {
  return `${(score * 100).toFixed(1)}%`;
}

// Get similarity color
export function getSimilarityColor(score: number): string {
  if (score >= 0.8) return 'text-success-600';
  if (score >= 0.6) return 'text-warning-600';
  return 'text-error-600';
}

// Generate sample data
export function generateSampleData() {
  return {
    files: [
      {
        file_id: 'sample_1',
        filename: 'privacy_policy.pdf',
        file_path: '/uploads/sample_1_privacy_policy.pdf',
        content_type: 'application/pdf',
        size: 1024000,
        uploaded_at: Date.now() - 3600000
      },
      {
        file_id: 'sample_2',
        filename: 'technical_specs.docx',
        file_path: '/uploads/sample_2_technical_specs.docx',
        content_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        size: 2048000,
        uploaded_at: Date.now() - 1800000
      }
    ],
    chunks: [
      {
        chunk_id: 'sample_1_chunk_0',
        text: 'PrivAI is a privacy-first AI application designed for educational institutions...',
        metadata: {
          source_file: 'privacy_policy.pdf',
          page_number: 1,
          chunk_index: 0,
          chunk_type: 'privacy_policy'
        }
      }
    ],
    chatMessages: [
      {
        id: 'sample_1',
        query: 'What is PrivAI?',
        answer: 'PrivAI is a privacy-first AI application designed for educational institutions...',
        sources: [],
        timestamp: Date.now() - 600000,
        metadata: {
          query: 'What is PrivAI?',
          retrieved_chunks: 0,
          processing_time: 0.5,
          model_used: 'mock',
          cached: false
        }
      }
    ]
  };
}
