import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  MessageSquare, 
  FileText, 
  Database,
  RefreshCw,
  Trash2,
  Download,
  Copy
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../components/Card';
import { Button } from '../components/Button';
import { Textarea } from '../components/Textarea';
import { Alert } from '../components/Alert';
import { ChatMessage } from '../components/ChatMessage';
import { useAppState } from '../hooks/useAppState';
import { useApi } from '../hooks/useApi';
import { generateId, copyToClipboard } from '../utils/helpers';
import { ChatMessage as ChatMessageType } from '../types';

interface ChatPageProps {
  onNavigate: (page: string) => void;
}

export const ChatPage: React.FC<ChatPageProps> = ({ onNavigate }) => {
  const { 
    appState, 
    addChatMessage, 
    clearChatHistory, 
    setError, 
    clearError 
  } = useAppState();
  
  const { sendChatMessage, isLoading, error } = useApi();
  
  const [query, setQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [appState.chatHistory]);

  // Focus textarea on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleSendMessage = async () => {
    if (!query.trim() || isLoading) return;

    const userQuery = query.trim();
    setQuery('');
    setIsTyping(true);

    try {
      clearError();
      
      // Add user message to history
      const userMessage: ChatMessageType = {
        id: generateId(),
        query: userQuery,
        answer: '',
        sources: [],
        timestamp: Date.now(),
        metadata: {
          query: userQuery,
          retrieved_chunks: 0,
          processing_time: 0,
          model_used: 'mock',
          cached: false
        }
      };
      
      addChatMessage(userMessage);

      // Send to API
      const response = await sendChatMessage(userQuery);
      
      if (response) {
        // Update the message with the response
        const updatedMessage: ChatMessageType = {
          ...userMessage,
          answer: response.answer,
          sources: response.sources,
          metadata: response.metadata
        };
        
        // Remove the temporary message and add the complete one
        addChatMessage(updatedMessage);
      } else {
        setError('Failed to get response. Please try again.');
      }
    } catch (err) {
      setError('Failed to send message. Please try again.');
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearHistory = () => {
    clearChatHistory();
  };

  const handleExportHistory = () => {
    const historyText = appState.chatHistory
      .map(msg => `Q: ${msg.query}\nA: ${msg.answer}\n\n`)
      .join('');
    
    const blob = new Blob([historyText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `privai-chat-history-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleCopyAll = async () => {
    const allText = appState.chatHistory
      .map(msg => `Q: ${msg.query}\nA: ${msg.answer}`)
      .join('\n\n');
    
    await copyToClipboard(allText);
  };

  const hasData = appState.uploadedFiles.length > 0 || appState.processedChunks.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            PrivAI Chat
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Ask questions about your uploaded documents and get AI-powered answers with source references.
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

        {/* No Data Warning */}
        {!hasData && (
          <div className="mb-6">
            <Alert type="warning">
              No data available for chat. Please upload files or connect to a database first.
              <Button
                onClick={() => onNavigate('upload')}
                variant="outline"
                size="sm"
                className="ml-4"
              >
                Go to Upload
              </Button>
            </Alert>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <Card className="h-[600px] flex flex-col">
              <CardHeader className="flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center space-x-2">
                      <MessageSquare className="h-5 w-5 text-primary-600" />
                      <span>Chat with PrivAI</span>
                    </CardTitle>
                    <CardDescription>
                      Ask questions about your documents
                    </CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      onClick={handleCopyAll}
                      variant="ghost"
                      size="sm"
                      title="Copy all messages"
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={handleExportHistory}
                      variant="ghost"
                      size="sm"
                      title="Export chat history"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      onClick={handleClearHistory}
                      variant="ghost"
                      size="sm"
                      title="Clear chat history"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="flex-1 overflow-hidden">
                {/* Messages */}
                <div className="h-full overflow-y-auto space-y-6 pr-2">
                  {appState.chatHistory.length === 0 ? (
                    <div className="h-full flex items-center justify-center">
                      <div className="text-center">
                        <Bot className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          Start a conversation
                        </h3>
                        <p className="text-gray-600">
                          Ask questions about your uploaded documents
                        </p>
                      </div>
                    </div>
                  ) : (
                    appState.chatHistory.map((message) => (
                      <ChatMessage key={message.id} message={message} />
                    ))
                  )}
                  
                  {/* Typing indicator */}
                  {isTyping && (
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-success-100 rounded-full flex items-center justify-center">
                        <Bot className="h-4 w-4 text-success-600" />
                      </div>
                      <div className="flex-1">
                        <div className="bg-white border rounded-lg p-4">
                          <div className="flex items-center space-x-2">
                            <RefreshCw className="h-4 w-4 text-primary-600 animate-spin" />
                            <span className="text-sm text-gray-600">PrivAI is thinking...</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>
              </CardContent>
              
              {/* Input Area */}
              <div className="flex-shrink-0 p-6 border-t">
                <div className="flex space-x-4">
                  <Textarea
                    ref={textareaRef}
                    placeholder="Ask a question about your documents..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={isLoading || !hasData}
                    className="flex-1 min-h-[60px] max-h-[120px] resize-none"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!query.trim() || isLoading || !hasData}
                    loading={isLoading}
                    className="self-end"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Data Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Data Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-600">Files</span>
                  </div>
                  <span className="font-medium">{appState.uploadedFiles.length}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Database className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-600">Chunks</span>
                  </div>
                  <span className="font-medium">{appState.processedChunks.length}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <MessageSquare className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-600">Messages</span>
                  </div>
                  <span className="font-medium">{appState.chatHistory.length}</span>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  onClick={() => onNavigate('upload')}
                  variant="outline"
                  className="w-full justify-start"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  Upload Files
                </Button>
                
                <Button
                  onClick={() => onNavigate('ingestion')}
                  variant="outline"
                  className="w-full justify-start"
                >
                  <Database className="h-4 w-4 mr-2" />
                  Process Data
                </Button>
                
                <Button
                  onClick={handleClearHistory}
                  variant="outline"
                  className="w-full justify-start"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear History
                </Button>
              </CardContent>
            </Card>

            {/* Sample Questions */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Sample Questions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <button
                  onClick={() => setQuery('What is this document about?')}
                  className="w-full text-left text-sm text-primary-600 hover:text-primary-700 p-2 rounded hover:bg-primary-50"
                >
                  What is this document about?
                </button>
                <button
                  onClick={() => setQuery('Summarize the key points')}
                  className="w-full text-left text-sm text-primary-600 hover:text-primary-700 p-2 rounded hover:bg-primary-50"
                >
                  Summarize the key points
                </button>
                <button
                  onClick={() => setQuery('What are the main topics?')}
                  className="w-full text-left text-sm text-primary-600 hover:text-primary-700 p-2 rounded hover:bg-primary-50"
                >
                  What are the main topics?
                </button>
                <button
                  onClick={() => setQuery('Find information about...')}
                  className="w-full text-left text-sm text-primary-600 hover:text-primary-700 p-2 rounded hover:bg-primary-50"
                >
                  Find information about...
                </button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
