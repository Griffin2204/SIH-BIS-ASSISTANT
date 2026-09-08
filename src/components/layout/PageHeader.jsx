import React from 'react';
import './PageHeader.css';
import { ChevronRight } from 'lucide-react';

export function PageHeader({
  title,
  description,
  breadcrumbs = [],
  actions,
  badge: BadgeComponent = null,
  className = ''
}) {
  return (
    <div className={`page-header ${className}`}>
      {breadcrumbs.length > 0 && (
        <nav className="breadcrumbs" aria-label="Breadcrumb">
          {breadcrumbs.map((breadcrumb, idx) => (
            <React.Fragment key={idx}>
              {idx > 0 && <ChevronRight size={14} className="breadcrumb-separator" />}
              <span className={`breadcrumb-item ${idx === breadcrumbs.length - 1 ? 'active' : ''}`}>
                {breadcrumb}
              </span>
            </React.Fragment>
          ))}
        </nav>
      )}

      <div className="page-header-content">
        <div className="page-header-text">
          <div className="page-title-row">
            <h1 className="page-title">{title}</h1>
            {BadgeComponent}
          </div>
          {description && <p className="page-description">{description}</p>}
        </div>

        {actions && <div className="page-header-actions">{actions}</div>}
      </div>
    </div>
  );
}

export default PageHeader;
