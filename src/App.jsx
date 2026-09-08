import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext';
import DashboardLayout from './components/layout/DashboardLayout';
import DashboardPage from './pages/DashboardPage';
import KnowPage from './pages/KnowPage';
import ComplyPage from './pages/ComplyPage';
import VerifyPage from './pages/VerifyPage';
import DocumentsPage from './pages/DocumentsPage';
import FeedbackPage from './pages/FeedbackPage';
import ProducerDashboardPage from './pages/ProducerDashboardPage';
import ConsumerDashboardPage from './pages/ConsumerDashboardPage';

function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<DashboardPage />} />

            {/* KNOW Mode Routes */}
            <Route path="know" element={<KnowPage defaultSubTab="chat" />} />
            <Route path="know/chat" element={<KnowPage defaultSubTab="chat" />} />
            <Route path="know/search" element={<KnowPage defaultSubTab="search" />} />
            <Route path="know/discovery" element={<KnowPage defaultSubTab="discovery" />} />
            <Route path="know/faq" element={<KnowPage defaultSubTab="faq" />} />
            <Route path="chatbot" element={<KnowPage defaultSubTab="chat" />} />
            <Route path="standards" element={<KnowPage defaultSubTab="search" />} />

            {/* COMPLY Mode Routes */}
            <Route path="comply" element={<ComplyPage defaultSubTab="dashboard" />} />
            <Route path="comply/dashboard" element={<ProducerDashboardPage />} />
            <Route path="comply/analyzer" element={<ComplyPage defaultSubTab="analyzer" />} />
            <Route path="comply/prefill" element={<ComplyPage defaultSubTab="prefill" />} />
            <Route path="comply/tracker" element={<ComplyPage defaultSubTab="tracker" />} />

            {/* VERIFY Mode Routes */}
            <Route path="verify" element={<VerifyPage defaultSubTab="dashboard" />} />
            <Route path="verify/dashboard" element={<ConsumerDashboardPage />} />
            <Route path="verify/licence" element={<VerifyPage defaultSubTab="licence" />} />
            <Route path="verify/huid" element={<VerifyPage defaultSubTab="huid" />} />
            <Route path="verify/fake-detector" element={<VerifyPage defaultSubTab="fake-detector" />} />
            <Route path="verification" element={<VerifyPage defaultSubTab="licence" />} />

            {/* Document Upload & Utilities */}
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="feedback" element={<FeedbackPage />} />

            {/* Fallback Catch-All */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  );
}

export default App;
