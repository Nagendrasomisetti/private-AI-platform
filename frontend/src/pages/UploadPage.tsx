import React, { useState } from 'react';
import { Upload, Database, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/Card';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Alert } from '../components/Alert';
import { FileUpload } from '../components/FileUpload';
import { useAppState } from '../hooks/useAppState';
import { useApi } from '../hooks/useApi';
import { UploadedFile } from '../types';

interface UploadPageProps {
  onNavigate: (page: string) => void;
}

export const UploadPage: React.FC<UploadPageProps> = ({ onNavigate }) => {
  const { appState, addUploadedFile, removeUploadedFile, setError, clearError } = useAppState();
  const { uploadFile, connectDatabase, isLoading, error } = useApi();
  
  const [dbUrl, setDbUrl] = useState('');
  const [dbConnected, setDbConnected] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleFileUpload = async (file: File) => {
    try {
      clearError();
      const uploadedFile = await uploadFile(file);
      
      if (uploadedFile) {
        addUploadedFile(uploadedFile);
        setUploadSuccess(true);
        setTimeout(() => setUploadSuccess(false), 3000);
      }
    } catch (err) {
      setError('Failed to upload file. Please try again.');
    }
  };

  const handleFileRemove = (fileId: string) => {
    removeUploadedFile(fileId);
  };

  const handleDatabaseConnect = async () => {
    if (!dbUrl.trim()) {
      setError('Please enter a database URL');
      return;
    }

    try {
      clearError();
      const success = await connectDatabase(dbUrl);
      
      if (success) {
        setDbConnected(true);
        setError(null);
      } else {
        setError('Failed to connect to database. Please check your URL.');
      }
    } catch (err) {
      setError('Database connection failed. Please try again.');
    }
  };

  const handleStartIngestion = () => {
    if (appState.uploadedFiles.length === 0 && !dbConnected) {
      setError('Please upload files or connect to a database first');
      return;
    }
    
    onNavigate('ingestion');
  };

  const totalFileSize = appState.uploadedFiles.reduce((total, file) => total + file.size, 0);
  const fileCount = appState.uploadedFiles.length;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Upload Files & Connect Database
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload your college documents or connect to a database to get started with PrivAI.
            All data is processed locally for complete privacy.
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
        {uploadSuccess && (
          <div className="mb-6">
            <Alert type="success">
              File uploaded successfully!
            </Alert>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* File Upload Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="h-5 w-5 text-primary-600" />
                <span>Upload Files</span>
              </CardTitle>
              <CardDescription>
                Upload PDF, CSV, or DOCX files from your computer
              </CardDescription>
            </CardHeader>
            
            <CardContent>
              <FileUpload
                onFileSelect={handleFileUpload}
                onFileRemove={handleFileRemove}
                uploadedFiles={appState.uploadedFiles}
                isUploading={isLoading}
              />
            </CardContent>
            
            <CardFooter>
              <div className="w-full">
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Files: {fileCount}</span>
                  <span>Total size: {(totalFileSize / 1024 / 1024).toFixed(2)} MB</span>
                </div>
              </div>
            </CardFooter>
          </Card>

          {/* Database Connection Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5 text-primary-600" />
                <span>Connect Database</span>
              </CardTitle>
              <CardDescription>
                Connect to your college database for data ingestion
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <Input
                label="Database URL"
                placeholder="postgresql://user:password@localhost:5432/database"
                value={dbUrl}
                onChange={(e) => setDbUrl(e.target.value)}
                helperText="Supported: PostgreSQL, MySQL, SQLite, MongoDB"
              />
              
              <Button
                onClick={handleDatabaseConnect}
                loading={isLoading}
                className="w-full"
                variant={dbConnected ? 'success' : 'primary'}
              >
                {dbConnected ? (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Connected
                  </>
                ) : (
                  'Connect to Database'
                )}
              </Button>
            </CardContent>
            
            <CardFooter>
              <div className="w-full">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  {dbConnected ? (
                    <>
                      <CheckCircle className="h-4 w-4 text-success-600" />
                      <span>Database connected successfully</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="h-4 w-4 text-warning-600" />
                      <span>No database connection</span>
                    </>
                  )}
                </div>
              </div>
            </CardFooter>
          </Card>
        </div>

        {/* Summary Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-primary-600" />
              <span>Ready for Ingestion</span>
            </CardTitle>
            <CardDescription>
              Review your uploaded files and database connection before starting ingestion
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Files Summary */}
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-primary-600 mb-2">
                  {fileCount}
                </div>
                <div className="text-sm text-gray-600">
                  Files Uploaded
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {(totalFileSize / 1024 / 1024).toFixed(2)} MB total
                </div>
              </div>

              {/* Database Status */}
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-success-600 mb-2">
                  {dbConnected ? '✓' : '✗'}
                </div>
                <div className="text-sm text-gray-600">
                  Database Status
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {dbConnected ? 'Connected' : 'Not connected'}
                </div>
              </div>

              {/* Ready Status */}
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-warning-600 mb-2">
                  {(fileCount > 0 || dbConnected) ? '✓' : '✗'}
                </div>
                <div className="text-sm text-gray-600">
                  Ready to Process
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {(fileCount > 0 || dbConnected) ? 'Ready' : 'Upload files or connect DB'}
                </div>
              </div>
            </div>
          </CardContent>
          
          <CardFooter>
            <Button
              onClick={handleStartIngestion}
              disabled={fileCount === 0 && !dbConnected}
              className="w-full"
              size="lg"
            >
              Start Data Ingestion
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default UploadPage;
