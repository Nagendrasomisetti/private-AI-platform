import React from 'react';
import { cn } from '../utils/helpers';
import { AlertType } from '../types';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: AlertType;
  title?: string;
  children: React.ReactNode;
  onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({
  type = 'info',
  title,
  children,
  onClose,
  className,
  ...props
}) => {
  const typeClasses = {
    success: 'bg-success-50 border-success-200 text-success-800',
    warning: 'bg-warning-50 border-warning-200 text-warning-800',
    error: 'bg-error-50 border-error-200 text-error-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  const iconClasses = {
    success: 'text-success-600',
    warning: 'text-warning-600',
    error: 'text-error-600',
    info: 'text-blue-600'
  };

  const icons = {
    success: '✅',
    warning: '⚠️',
    error: '❌',
    info: 'ℹ️'
  };

  return (
    <div
      className={cn(
        'relative rounded-lg border p-4',
        typeClasses[type],
        className
      )}
      {...props}
    >
      <div className="flex items-start">
        <div className={cn('text-lg mr-3', iconClasses[type])}>
          {icons[type]}
        </div>
        <div className="flex-1">
          {title && (
            <h4 className="font-semibold mb-1">
              {title}
            </h4>
          )}
          <div className="text-sm">
            {children}
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-3 text-lg hover:opacity-70 transition-opacity"
            aria-label="Close alert"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
};

export default Alert;
