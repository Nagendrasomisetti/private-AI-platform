import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  Database, 
  MessageSquare, 
  Menu, 
  X,
  Shield,
  Lock
} from 'lucide-react';
import { Button } from './components/Button';
import { Card } from './components/Card';
import { Alert } from './components/Alert';
import { PrivacyIndicator } from './components/PrivacyIndicator';
import { useAppState } from './hooks/useAppState';
import { useApi } from './hooks/useApi';
import UploadPage from './pages/UploadPage';
import IngestionPage from './pages/IngestionPage';
import ChatPage from './pages/ChatPage';
import { generateSampleData } from './utils/helpers';

const App: React.FC = () => {
  const { appState, navigateToPage, updateAppState } = useAppState();
  const { checkHealth } = useApi();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  // Check API status on mount
  useEffect(() => {
    const checkApi = async () => {
      try {
        const isOnline = await checkHealth();
        setApiStatus(isOnline ? 'online' : 'offline');
      } catch (error) {
        setApiStatus('offline');
      }
    };

    checkApi();
  }, [checkHealth]);

  // Navigation items
  const navigationItems = [
    {
      id: 'upload',
      name: 'Upload & Connect',
      icon: Upload,
      description: 'Upload files and connect to database'
    },
    {
      id: 'ingestion',
      name: 'Data Ingestion',
      icon: Database,
      description: 'Process and ingest your data'
    },
    {
      id: 'chat',
      name: 'AI Chat',
      icon: MessageSquare,
      description: 'Chat with your documents'
    }
  ];

  const handleNavigate = (page: string) => {
    navigateToPage(page);
    setSidebarOpen(false);
  };

  const handleLoadSampleData = () => {
    const sampleData = generateSampleData();
    updateAppState({
      uploadedFiles: sampleData.files,
      processedChunks: sampleData.chunks,
      chatHistory: sampleData.chatMessages
    });
  };

  const renderPage = () => {
    switch (appState.currentPage) {
      case 'upload':
        return <UploadPage onNavigate={handleNavigate} />;
      case 'ingestion':
        return <IngestionPage onNavigate={handleNavigate} />;
      case 'chat':
        return <ChatPage onNavigate={handleNavigate} />;
      default:
        return <UploadPage onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Privacy Indicator */}
      <PrivacyIndicator />
      
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:inset-0
      `}>
        <div className="flex items-center justify-between h-16 px-6 border-b">
          <div className="flex items-center space-x-2">
            <Shield className="h-8 w-8 text-primary-600" />
            <h1 className="text-xl font-bold text-gray-900">PrivAI</h1>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="mt-6 px-3">
          <div className="space-y-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = appState.currentPage === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavigate(item.id)}
                  className={`
                    w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                    ${isActive 
                      ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-600' 
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    }
                  `}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  <div className="text-left">
                    <div>{item.name}</div>
                    <div className="text-xs text-gray-500">{item.description}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </nav>

        {/* API Status */}
        <div className="absolute bottom-4 left-4 right-4">
          <Card className="p-3">
            <div className="flex items-center space-x-2">
              <div className={`
                w-2 h-2 rounded-full
                ${apiStatus === 'online' ? 'bg-success-500' : 
                  apiStatus === 'offline' ? 'bg-error-500' : 'bg-warning-500'}
              `} />
              <span className="text-xs text-gray-600">
                {apiStatus === 'online' ? 'API Online' : 
                 apiStatus === 'offline' ? 'API Offline' : 'Checking...'}
              </span>
            </div>
          </Card>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Bar */}
        <div className="sticky top-0 z-30 bg-white border-b shadow-sm">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600"
            >
              <Menu className="h-6 w-6" />
            </button>
            
            <div className="flex items-center space-x-4">
              <div className="hidden sm:block">
                <h2 className="text-lg font-semibold text-gray-900">
                  {navigationItems.find(item => item.id === appState.currentPage)?.name}
                </h2>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button
                  onClick={handleLoadSampleData}
                  variant="outline"
                  size="sm"
                >
                  Load Sample Data
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <main>
          {renderPage()}
        </main>
      </div>

      {/* API Status Alert */}
      {apiStatus === 'offline' && (
        <div className="fixed bottom-4 right-4 z-50">
          <Alert type="error" title="API Offline">
            Cannot connect to the backend API. Please make sure the server is running.
          </Alert>
        </div>
      )}
    </div>
  );
};

export default App;
