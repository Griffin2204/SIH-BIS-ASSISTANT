import React from 'react';
import './ErrorState.css';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export function ErrorState({
  title = 'An error occurred',
  message = 'Unable to complete your request. Please try again.',
  onRetry,
  retryLabel = 'Try Again',
  className = ''
}) {
  return (
    <div className={`error-state ${className}`}>
      <div className="error-state-icon">
        <AlertTriangle size={32} />
      </div>
      <div className="error-state-content">
        <h4 className="error-state-title">{title}</h4>
        <p className="error-state-message">{message}</p>
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" icon={RefreshCw} onClick={onRetry} className="error-retry-btn">
          {retryLabel}
        </Button>
      )}
    </div>
  );
}

export default ErrorState;
