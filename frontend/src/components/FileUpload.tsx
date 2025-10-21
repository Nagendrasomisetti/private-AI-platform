import React, { useCallback, useState } from 'react';
import { Upload, File, X, CheckCircle } from 'lucide-react';
import { cn, formatFileSize, getFileIcon, validateFileType, validateFileSize } from '../utils/helpers';
import { UploadedFile } from '../types';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove: (fileId: string) => void;
  uploadedFiles: UploadedFile[];
  isUploading: boolean;
  maxFileSize?: number; // in MB
  acceptedTypes?: string[];
  className?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onFileRemove,
  uploadedFiles,
  isUploading,
  maxFileSize = 100, // 100MB default
  acceptedTypes = ['application/pdf', 'text/csv', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  className
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError(null);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      handleFile(file);
    }
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setError(null);

    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      handleFile(file);
    }
  }, []);

  const handleFile = useCallback((file: File) => {
    // Validate file type
    if (!validateFileType(file, acceptedTypes)) {
      setError(`File type not supported. Please upload: ${acceptedTypes.join(', ')}`);
      return;
    }

    // Validate file size
    if (!validateFileSize(file, maxFileSize)) {
      setError(`File too large. Maximum size: ${maxFileSize}MB`);
      return;
    }

    onFileSelect(file);
  }, [acceptedTypes, maxFileSize, onFileSelect]);

  const handleRemoveFile = useCallback((fileId: string) => {
    onFileRemove(fileId);
  }, [onFileRemove]);

  return (
    <div className={cn('w-full', className)}>
      {/* Upload Area */}
      <div
        className={cn(
          'relative border-2 border-dashed rounded-lg p-8 text-center transition-colors',
          dragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-gray-400',
          isUploading && 'opacity-50 pointer-events-none'
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept={acceptedTypes.join(',')}
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={isUploading}
        />
        
        <div className="flex flex-col items-center space-y-4">
          <div className="p-4 bg-primary-100 rounded-full">
            <Upload className="h-8 w-8 text-primary-600" />
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {isUploading ? 'Uploading...' : 'Upload Files'}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Drag and drop files here, or click to select
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Supported: PDF, CSV, DOCX • Max size: {maxFileSize}MB
            </p>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-4 p-3 bg-error-50 border border-error-200 rounded-md">
          <p className="text-sm text-error-600">{error}</p>
        </div>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className="text-sm font-medium text-gray-900 mb-3">
            Uploaded Files ({uploadedFiles.length})
          </h4>
          <div className="space-y-2">
            {uploadedFiles.map((file) => (
              <div
                key={file.file_id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">
                    {getFileIcon(file.filename)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {file.filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(file.size)} • {formatTimestamp(file.uploaded_at)}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-success-600" />
                  <button
                    onClick={() => handleRemoveFile(file.file_id)}
                    className="p-1 text-gray-400 hover:text-error-600 transition-colors"
                    disabled={isUploading}
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Helper function for timestamp formatting
function formatTimestamp(timestamp: number): string {
  return new Date(timestamp).toLocaleString();
}

export default FileUpload;
