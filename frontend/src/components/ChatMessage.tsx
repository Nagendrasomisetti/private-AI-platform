import React, { useState } from 'react';
import { User, Bot, Copy, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { cn, formatSimilarityScore, getSimilarityColor, copyToClipboard } from '../utils/helpers';
import { ChatMessage as ChatMessageType, Source } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
  className?: string;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  className
}) => {
  const [showSources, setShowSources] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const success = await copyToClipboard(message.answer);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const toggleSources = () => {
    setShowSources(!showSources);
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* User Query */}
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
          <User className="h-4 w-4 text-primary-600" />
        </div>
        <div className="flex-1">
          <div className="bg-gray-100 rounded-lg p-4">
            <p className="text-gray-900">{message.query}</p>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {new Date(message.timestamp).toLocaleString()}
          </p>
        </div>
      </div>

      {/* Bot Response */}
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 w-8 h-8 bg-success-100 rounded-full flex items-center justify-center">
          <Bot className="h-4 w-4 text-success-600" />
        </div>
        <div className="flex-1">
          <div className="bg-white border rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-gray-900 whitespace-pre-wrap">
                  {message.answer}
                </p>
              </div>
              <button
                onClick={handleCopy}
                className="ml-2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
                title="Copy answer"
              >
                {copied ? (
                  <CheckCircle className="h-4 w-4 text-success-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </button>
            </div>
            
            {/* Metadata */}
            <div className="mt-3 pt-3 border-t border-gray-100">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center space-x-4">
                  <span>Processing: {message.metadata.processing_time.toFixed(2)}s</span>
                  <span>Model: {message.metadata.model_used}</span>
                  {message.metadata.cached && (
                    <span className="text-success-600">Cached</span>
                  )}
                </div>
                <span>{message.metadata.retrieved_chunks} sources</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sources */}
      {message.sources.length > 0 && (
        <div className="ml-11">
          <button
            onClick={toggleSources}
            className="flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-700 transition-colors"
          >
            <span>
              {showSources ? 'Hide' : 'Show'} Sources ({message.sources.length})
            </span>
            {showSources ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </button>
          
          {showSources && (
            <div className="mt-3 space-y-3">
              {message.sources.map((source, index) => (
                <SourceCard key={index} source={source} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

interface SourceCardProps {
  source: Source;
}

const SourceCard: React.FC<SourceCardProps> = ({ source }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-gray-50 border rounded-lg p-3">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-sm font-medium text-gray-900">
              Source {source.rank}
            </span>
            <span className={cn(
              'text-xs px-2 py-1 rounded-full',
              getSimilarityColor(source.similarity_score)
            )}>
              {formatSimilarityScore(source.similarity_score)}
            </span>
          </div>
          
          <div className="text-sm text-gray-600">
            <p className="font-medium">
              {source.metadata.source_file}
              {source.metadata.page_number && (
                <span className="text-gray-500"> (Page {source.metadata.page_number})</span>
              )}
            </p>
            
            <p className="mt-1 text-gray-700">
              {expanded ? source.text : `${source.text.substring(0, 200)}...`}
            </p>
            
            {source.text.length > 200 && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-primary-600 hover:text-primary-700 text-xs mt-1"
              >
                {expanded ? 'Show less' : 'Show more'}
              </button>
            )}
          </div>
        </div>
        
        <button
          onClick={() => window.open(`#source-${source.rank}`, '_blank')}
          className="ml-2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
          title="Open source"
        >
          <ExternalLink className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

// Import CheckCircle for the copied state
import { CheckCircle } from 'lucide-react';

export default ChatMessage;
