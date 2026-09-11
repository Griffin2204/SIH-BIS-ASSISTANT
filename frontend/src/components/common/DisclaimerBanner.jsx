import React from 'react';
import './DisclaimerBanner.css';
import { ShieldCheck } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export function DisclaimerBanner({ className = '' }) {
  const { t } = useLanguage();

  return (
    <div className={`disclaimer-banner ${className}`}>
      <div className="disclaimer-icon">
        <ShieldCheck size={18} />
      </div>
      <div className="disclaimer-text">
        <span className="disclaimer-title">{t('disclaimerTitle')}</span>
        <span className="disclaimer-body">{t('disclaimerBody')}</span>
      </div>
    </div>
  );
}

export default DisclaimerBanner;
