import React, { createContext, useContext, useState } from 'react';

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

const TRANSLATIONS = {
  en: {
    appTitle: 'BIS AI Assistant',
    portalSub: 'GovTech Compliance & Verification Portal',
    navKnow: 'KNOW (Discovery & Chat)',
    navComply: 'COMPLY (Producer Hub)',
    navVerify: 'VERIFY (Consumer Portal)',
    searchPlaceholder: 'Search Indian Standards (IS 10500, IS 694)...',
    askAiBtn: 'Ask AI Assistant',
    verifyBtn: 'Verify Credentials',
    uploadBtn: 'Upload Documents',
    disclaimer: 'Official BIS Assistance Portal — Powered by Guardrailed RAG AI',
    disclaimerNotice: 'Never invents standard numbers or licence details. Mock data used until live backend connected.'
  },
  hi: {
    appTitle: 'बीआईएस एआई सहायक',
    portalSub: 'सरकारी मानक एवं सत्यापन पोर्टल',
    navKnow: 'जानें (खोज एवं चैट)',
    navComply: 'अनुपालन (उत्पादक हब)',
    navVerify: 'सत्यापित करें (उपभोक्ता पोर्टल)',
    searchPlaceholder: 'भारतीय मानक खोजें (IS 10500, IS 694)...',
    askAiBtn: 'एआई सहायक से पूछें',
    verifyBtn: 'प्रमाणपत्र जांचें',
    uploadBtn: 'दस्तावेज़ अपलोड करें',
    disclaimer: 'आधिकारिक बीआईएस सहायता पोर्टल',
    disclaimerNotice: 'मानक संख्या या लाइसेंस विवरण कभी मनगढ़ंत नहीं बनाता।'
  },
  mr: {
    appTitle: 'बीआयएस एआय सहाय्यक',
    portalSub: 'शासकीय मानके आणि पडताळणी पोर्टल',
    navKnow: 'जाणून घ्या (शोध आणि चॅट)',
    navComply: 'पालन करा (उत्पादक हब)',
    navVerify: 'पडताळणी करा (ग्राहक पोर्टल)',
    searchPlaceholder: 'भारतीय मानके शोधा (IS 10500, IS 694)...',
    askAiBtn: 'एआय सहाय्यकाला विचारा',
    verifyBtn: 'प्रमाणपत्र तपासा',
    uploadBtn: 'कागदपत्रे अपलोड करा',
    disclaimer: 'अधिकृत बीआयएस सहाय्यक पोर्टल',
    disclaimerNotice: 'मानक क्रमांक किंवा परवाना तपशील तयार करत नाही.'
  }
};

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [currentLang, setCurrentLang] = useState('en');

  const t = (key) => {
    const dict = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
    return dict[key] || TRANSLATIONS.en[key] || key;
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
