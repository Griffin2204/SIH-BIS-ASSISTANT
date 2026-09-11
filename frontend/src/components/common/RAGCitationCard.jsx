import React, { useState } from 'react';
import './RAGCitationCard.css';
import { ExternalLink, ShieldCheck, ThumbsDown, AlertCircle, FileText } from 'lucide-react';
import Badge from '../ui/Badge';

export function RAGCitationCard({ citation, confidenceScore, confidenceLabel }) {
  const [feedbackSent, setFeedbackSent] = useState(false);

  const displayTitle = citation.filename || citation.title || 'Document Source';
  const fileType = (citation.file_type || 'txt').toUpperCase();
  const chunkIndex = citation.chunk_index !== undefined ? citation.chunk_index : null;
  const similarity = citation.similarity_score !== undefined ? citation.similarity_score : confidenceScore;
  
  let pagesStr = null;
  if (Array.isArray(citation.pages) && citation.pages.length > 0) {
    const validPages = citation.pages.filter(p => p > 0);
    if (validPages.length > 0) {
      pagesStr = `Page ${validPages.join(', ')}`;
    }
  } else if (typeof citation.pages === 'number' && citation.pages > 0) {
    pagesStr = `Page ${citation.pages}`;
  } else if (citation.section) {
    pagesStr = citation.section;
  }

  const badgeText = confidenceLabel || (similarity !== undefined && similarity !== null ? `${(similarity * 100).toFixed(1)}% relevance` : null);
  const badgeVariant = similarity >= 0.8 ? 'success' : similarity >= 0.5 ? 'info' : 'warning';

  return (
    <div className="rag-citation-card">
      <div className="rag-citation-header">
        <div className="rag-source-title-group">
          <ShieldCheck size={16} className="rag-verified-icon" />
          <span className="rag-source-title">{displayTitle}</span>
        </div>
        {badgeText && (
          <Badge variant={badgeVariant} size="sm" dot>
            {badgeText}
          </Badge>
        )}
      </div>

      <div className="rag-citation-details">
        {citation.standardCode && (
          <div className="rag-detail-item">
            <span className="rag-detail-label">Standard Code:</span>
            <span className="rag-detail-code">{citation.standardCode}</span>
          </div>
        )}

        <div className="rag-detail-item">
          <span className="rag-detail-label">Format:</span>
          <span className="rag-detail-val">{fileType}</span>
        </div>

        {chunkIndex !== null && (
          <div className="rag-detail-item">
            <span className="rag-detail-label">Chunk:</span>
            <span className="rag-detail-val">Chunk {chunkIndex}</span>
          </div>
        )}

        {pagesStr && (
          <div className="rag-detail-item">
            <span className="rag-detail-label">Page:</span>
            <span className="rag-detail-val">{pagesStr}</span>
          </div>
        )}
      </div>

      {citation.snippet && (
        <div className="rag-citation-snippet" style={{ marginTop: '8px', fontSize: '0.82rem', color: 'var(--text-secondary, #475569)', fontStyle: 'italic', background: 'rgba(241, 245, 249, 0.6)', padding: '6px 10px', borderRadius: '4px', borderLeft: '3px solid #3b82f6' }}>
          "{citation.snippet}"
        </div>
      )}

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
