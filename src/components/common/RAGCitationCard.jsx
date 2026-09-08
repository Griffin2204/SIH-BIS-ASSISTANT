import React, { useState } from 'react';
import './RAGCitationCard.css';
import { ExternalLink, ShieldCheck, ThumbsDown, AlertCircle, FileText } from 'lucide-react';
import Badge from '../ui/Badge';

export function RAGCitationCard({ citation, confidenceScore, confidenceLabel }) {
  const [feedbackSent, setFeedbackSent] = useState(false);

  return (
    <div className="rag-citation-card">
      <div className="rag-citation-header">
        <div className="rag-source-title-group">
          <ShieldCheck size={16} className="rag-verified-icon" />
          <span className="rag-source-title">{citation.title}</span>
        </div>
        {confidenceLabel && (
          <Badge
            variant={confidenceScore >= 0.9 ? 'success' : confidenceScore >= 0.75 ? 'info' : 'warning'}
            size="sm"
            dot
          >
            {confidenceLabel}
          </Badge>
        )}
      </div>

      <div className="rag-citation-details">
        <div className="rag-detail-item">
          <span className="rag-detail-label">Standard Code:</span>
          <span className="rag-detail-code">{citation.standardCode}</span>
        </div>

        {citation.section && (
          <div className="rag-detail-item">
            <span className="rag-detail-label">Page / Section:</span>
            <span className="rag-detail-val">{citation.section}</span>
          </div>
        )}
      </div>

      <div className="rag-citation-actions">
        {citation.url && (
          <a
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
            className="rag-action-link"
          >
            <FileText size={14} />
            <span>View Official BIS PDF</span>
            <ExternalLink size={12} />
          </a>
        )}

        <button
          type="button"
          className={`rag-report-btn ${feedbackSent ? 'sent' : ''}`}
          onClick={() => setFeedbackSent(true)}
          disabled={feedbackSent}
        >
          <ThumbsDown size={13} />
          <span>{feedbackSent ? 'Reported to BIS' : 'Report Error'}</span>
        </button>
      </div>
    </div>
  );
}

export default RAGCitationCard;
