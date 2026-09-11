import React from 'react';
import './Badge.css';

export function Badge({
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
  icon: Icon = null,
  className = '',
  ...props
}) {
  return (
    <span className={`badge badge-${variant} badge-${size} ${className}`} {...props}>
      {dot && <span className="badge-dot" />}
      {Icon && <Icon className="badge-icon" size={size === 'sm' ? 12 : 14} />}
      <span>{children}</span>
    </span>
  );
}

export default Badge;
