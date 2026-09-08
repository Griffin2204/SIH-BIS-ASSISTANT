import React from 'react';
import './EmptyState.css';
import { FolderOpen } from 'lucide-react';
import { Button } from './Button';

export function EmptyState({
  icon: Icon = FolderOpen,
  title = 'No records found',
  description = 'There are no items to display at this moment.',
  actionLabel,
  onAction,
  className = ''
}) {
  return (
    <div className={`empty-state ${className}`}>
      <div className="empty-state-icon">
        <Icon size={36} />
      </div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-description">{description}</p>
      {actionLabel && onAction && (
        <Button variant="primary" size="md" onClick={onAction} className="empty-state-action">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

export default EmptyState;
