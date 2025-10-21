import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  CheckCircle, 
  AlertCircle, 
  FileText, 
  Database, 
  Trash2,
  RefreshCw,
  BarChart3
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/Card';
import { Button } from '../components/Button';
import { Alert } from '../components/Alert';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useAppState } from '../hooks/useAppState';
import { useApi } from '../hooks/useApi';
import { formatFileSize, formatTimestamp } from '../utils/helpers';

interface IngestionPageProps {
  onNavigate: (page: string) => void;
}

export const IngestionPage: React.FC<IngestionPageProps> = ({ onNavigate }) => {
  const { 
    appState, 
    addProcessedChunks, 
    clearAllChunks, 
    clearAllFiles, 
    setError, 
    clearError 
  } = useAppState();
  
  const { startIngestion, isLoading, error } = useApi();
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const [chunksProcessed, setChunksProcessed] = useState(0);
  const [processingTime, setProcessingTime] = useState(0);
  const [ingestionComplete, setIngestionComplete] = useState(false);

  // Simulate processing steps
  const processingSteps = [
    'Initializing processing...',
    'Reading uploaded files...',
    'Extracting text content...',
    'Creating text chunks...',
    'Generating embeddings...',
    'Storing in vector database...',
    'Finalizing ingestion...'
  ];

  const handleStartIngestion = async () => {
    if (appState.uploadedFiles.length === 0) {
      setError('No files uploaded. Please go back and upload some files first.');
      return;
    }

    try {
      clearError();
      setIsProcessing(true);
      setIngestionComplete(false);
      setChunksProcessed(0);
      setProcessingTime(0);
      
      // Simulate processing steps
      for (let i = 0; i < processingSteps.length; i++) {
        setProcessingStep(processingSteps[i]);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      // Start actual ingestion
      const chunks = await startIngestion();
      
      if (chunks) {
        addProcessedChunks(chunks);
        setChunksProcessed(chunks.length);
        setIngestionComplete(true);
      } else {
        setError('Ingestion failed. Please try again.');
      }
    } catch (err) {
      setError('Ingestion failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClearData = () => {
    clearAllChunks();
    clearAllFiles();
    setIngestionComplete(false);
    setChunksProcessed(0);
    setProcessingTime(0);
  };

  const handleGoToChat = () => {
    onNavigate('chat');
  };

  // Calculate processing time
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isProcessing) {
      interval = setInterval(() => {
        setProcessingTime(prev => prev + 1);
      }, 1000);
    }
    
    return () => clearInterval(interval);
  }, [isProcessing]);

  const totalFileSize = appState.uploadedFiles.reduce((total, file) => total + file.size, 0);
  const fileCount = appState.uploadedFiles.length;
  const chunkCount = appState.processedChunks.length;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Data Ingestion
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Process your uploaded files and database data into searchable chunks for AI analysis.
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6">
            <Alert type="error" onClose={clearError}>
              {error}
            </Alert>
          </div>
        )}

        {/* Success Alert */}
        {ingestionComplete && (
          <div className="mb-6">
            <Alert type="success">
              Data ingestion completed successfully! {chunksProcessed} chunks processed.
            </Alert>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Processing Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <RefreshCw className={`h-5 w-5 text-primary-600 ${isProcessing ? 'animate-spin' : ''}`} />
                <span>Processing Status</span>
              </CardTitle>
              <CardDescription>
                Monitor the ingestion process in real-time
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              {isProcessing ? (
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <LoadingSpinner size="md" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {processingStep}
                      </p>
                      <p className="text-xs text-gray-500">
                        Processing time: {processingTime}s
                      </p>
                    </div>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(processingTime / processingSteps.length) * 100}%` }}
                    />
                  </div>
                </div>
              ) : ingestionComplete ? (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 text-success-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Ingestion Complete!
                  </h3>
                  <p className="text-sm text-gray-600">
                    {chunksProcessed} chunks processed successfully
                  </p>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Play className="h-12 w-12 text-primary-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    Ready to Process
                  </h3>
                  <p className="text-sm text-gray-600">
                    Click start to begin data ingestion
                  </p>
                </div>
              )}
            </CardContent>
            
            <CardFooter>
              <Button
                onClick={handleStartIngestion}
                disabled={isProcessing || fileCount === 0}
                loading={isProcessing}
                className="w-full"
                variant={ingestionComplete ? 'success' : 'primary'}
              >
                {isProcessing ? 'Processing...' : ingestionComplete ? 'Process Again' : 'Start Ingestion'}
              </Button>
            </CardFooter>
          </Card>

          {/* Data Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-primary-600" />
                <span>Data Summary</span>
              </CardTitle>
              <CardDescription>
                Overview of your uploaded data and processing results
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-6">
                {/* Files Summary */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">Uploaded Files</h4>
                    <FileText className="h-4 w-4 text-gray-500" />
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Count:</span>
                      <span className="ml-2 font-medium">{fileCount}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Size:</span>
                      <span className="ml-2 font-medium">{formatFileSize(totalFileSize)}</span>
                    </div>
                  </div>
                </div>

                {/* Chunks Summary */}
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-900">Processed Chunks</h4>
                    <Database className="h-4 w-4 text-gray-500" />
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Count:</span>
                      <span className="ml-2 font-medium">{chunkCount}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Status:</span>
                      <span className={`ml-2 font-medium ${ingestionComplete ? 'text-success-600' : 'text-warning-600'}`}>
                        {ingestionComplete ? 'Complete' : 'Pending'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Processing Time */}
                {processingTime > 0 && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-gray-900">Processing Time</h4>
                      <RefreshCw className="h-4 w-4 text-gray-500" />
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-600">Duration:</span>
                      <span className="ml-2 font-medium">{processingTime}s</span>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* File List */}
        {appState.uploadedFiles.length > 0 && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Uploaded Files</CardTitle>
              <CardDescription>
                Files ready for processing
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-3">
                {appState.uploadedFiles.map((file) => (
                  <div
                    key={file.file_id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <FileText className="h-5 w-5 text-gray-500" />
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
                      {ingestionComplete && (
                        <CheckCircle className="h-4 w-4 text-success-600" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            onClick={handleClearData}
            variant="outline"
            className="sm:w-auto"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Clear All Data
          </Button>
          
          <Button
            onClick={handleGoToChat}
            disabled={!ingestionComplete}
            className="sm:w-auto"
          >
            Go to Chat
          </Button>
        </div>
      </div>
    </div>
  );
};

export default IngestionPage;
