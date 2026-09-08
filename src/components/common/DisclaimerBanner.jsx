import React from 'react';
import './DisclaimerBanner.css';
import { AlertCircle, ShieldCheck } from 'lucide-react';

export function DisclaimerBanner({ className = '' }) {
  return (
    <div className={`disclaimer-banner ${className}`}>
      <div className="disclaimer-icon">
        <ShieldCheck size={18} />
      </div>
      <div className="disclaimer-text">
        <span className="disclaimer-title">Official BIS Guardrailed Portal Notice:</span>
        <span className="disclaimer-body">
          Responses use verified RAG citations. Standard numbers and licence details are strictly verified against official BIS databases and never invented.
        </span>
      </div>
    </div>
  );
}

export default DisclaimerBanner;
