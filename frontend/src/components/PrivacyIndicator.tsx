import React from 'react';
import { Shield, Lock } from 'lucide-react';

interface PrivacyIndicatorProps {
  className?: string;
}

export const PrivacyIndicator: React.FC<PrivacyIndicatorProps> = ({
  className = ''
}) => {
  return (
    <div className={`privacy-indicator ${className}`}>
      <div className="flex items-center space-x-2">
        <Shield className="h-4 w-4" />
        <span className="font-medium">Privacy Protected</span>
        <Lock className="h-3 w-3" />
      </div>
      <div className="text-xs mt-1 opacity-90">
        All data processed locally
      </div>
    </div>
  );
};

export default PrivacyIndicator;
