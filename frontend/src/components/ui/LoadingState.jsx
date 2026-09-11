import React from 'react';
import './LoadingState.css';
import { Loader2 } from 'lucide-react';

export function LoadingState({
  message = 'Loading data...',
  variant = 'spinner', // 'spinner' | 'skeleton'
  count = 3,
  className = ''
}) {
  if (variant === 'skeleton') {
    return (
      <div className={`skeleton-container ${className}`}>
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="skeleton-card">
            <div className="skeleton-line skeleton-title" />
            <div className="skeleton-line skeleton-text" />
            <div className="skeleton-line skeleton-text short" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`loading-spinner-wrapper ${className}`}>
      <Loader2 className="loading-spinner animate-spin" size={32} />
      <p className="loading-message">{message}</p>
    </div>
  );
}

export default LoadingState;
