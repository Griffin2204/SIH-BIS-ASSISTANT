import React from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { Globe } from 'lucide-react';
import './MultilingualSelector.css';

export function MultilingualSelector({ className = '' }) {
  const { currentLang, setCurrentLang, LANGUAGES } = useLanguage();

  return (
    <div className={`lang-selector-wrapper ${className}`}>
      <Globe size={16} className="lang-icon" />
      <select
        value={currentLang}
        onChange={(e) => setCurrentLang(e.target.value)}
        className="lang-select"
        aria-label="Select Interface Language"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.nativeName} ({lang.name})
          </option>
        ))}
      </select>
    </div>
  );
}

export default MultilingualSelector;
