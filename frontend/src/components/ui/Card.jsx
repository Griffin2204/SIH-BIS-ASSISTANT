import React from 'react';
import './Card.css';

export function Card({
  children,
  title,
  subtitle,
  headerAction,
  footer,
  hoverable = false,
  className = '',
  padding = 'normal',
  ...props
}) {
  return (
    <div
      className={`card ${hoverable ? 'card-hoverable' : ''} card-padding-${padding} ${className}`}
      {...props}
    >
      {(title || subtitle || headerAction) && (
        <div className="card-header">
          <div className="card-header-titles">
            {title && <h3 className="card-title">{title}</h3>}
            {subtitle && <p className="card-subtitle">{subtitle}</p>}
          </div>
          {headerAction && <div className="card-header-action">{headerAction}</div>}
        </div>
      )}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
}

export default Card;
