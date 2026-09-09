import React, { createContext, useContext, useState, useEffect } from 'react';
import { TRANSLATIONS } from './translations';

export const LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ' },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ' },
  { code: 'as', name: 'Assamese', nativeName: 'অসমীয়া' },
];

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [currentLang, setCurrentLangState] = useState(() => {
    try {
      const saved = localStorage.getItem('sih_language');
      return saved && LANGUAGES.some((l) => l.code === saved) ? saved : 'en';
    } catch (e) {
      return 'en';
    }
  });

  const setCurrentLang = (newLang) => {
    try {
      localStorage.setItem('sih_language', newLang);
    } catch (e) {
      // Ignore storage errors
    }
    setCurrentLangState(newLang);
  };

  const t = (key) => {
    const langDict = TRANSLATIONS[currentLang];
    if (langDict && langDict[key] !== undefined) {
      return langDict[key];
    }
    const enDict = TRANSLATIONS.en;
    if (enDict && enDict[key] !== undefined) {
      return enDict[key];
    }
    return key;
  };

  return (
    <LanguageContext.Provider value={{ currentLang, setCurrentLang, t, LANGUAGES }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

export default LanguageContext;
