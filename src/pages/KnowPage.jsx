import React, { useState, useEffect } from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import SearchInput from '../components/ui/SearchInput';
import LoadingState from '../components/ui/LoadingState';
import EmptyState from '../components/ui/EmptyState';
import DisclaimerBanner from '../components/common/DisclaimerBanner';
import RAGCitationCard from '../components/common/RAGCitationCard';
import VoiceInputModal from '../components/common/VoiceInputModal';
import CameraCaptureModal from '../components/common/CameraCaptureModal';
import { sendChatMessage, searchStandards, recommendStandards } from '../api/client';
import { CATEGORIES } from '../data/mockStandards';
import { MOCK_SUGGESTED_QUESTIONS } from '../data/mockChat';
import { useLanguage } from '../context/LanguageContext';
import {
  Bot,
  Send,
  Trash2,
  Copy,
  Check,
  Mic,
  Camera,
  FileSearch,
  Sparkles,
  Compass,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  ShieldCheck
} from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import './KnowPage.css';

export function KnowPage({ defaultSubTab = 'chat' }) {
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(defaultSubTab);
  const { t } = useLanguage();

  useEffect(() => {
    if (searchParams.get('search')) {
      setActiveTab('search');
    }
  }, [searchParams]);

  return (
    <div className="know-page">
      <PageHeader
        title={`${t('navKnow')} — ${t('knowTitle')}`}
        description="Conversational AI guidance, semantic Indian Standards discovery, and trustworthy BIS regulatory repository."
        breadcrumbs={['Portal', t('navKnow')]}
        badge={<Badge variant="blue" dot>{t('ragGuardrailed')}</Badge>}
      />

      <DisclaimerBanner />

      {/* Mode Sub Tabs */}
      <div className="know-subtabs">
        <button
          type="button"
          className={`subtab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <Bot size={18} />
          <span>{t('navAskAi')}</span>
        </button>

        <button
          type="button"
          className={`subtab-btn ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          <FileSearch size={18} />
          <span>{t('navSmartSearch')}</span>
        </button>

        <button
          type="button"
          className={`subtab-btn ${activeTab === 'discovery' ? 'active' : ''}`}
          onClick={() => setActiveTab('discovery')}
        >
          <Sparkles size={18} />
          <span>{t('navDiscovery')}</span>
        </button>

        <button
          type="button"
          className={`subtab-btn ${activeTab === 'faq' ? 'active' : ''}`}
          onClick={() => setActiveTab('faq')}
        >
          <Compass size={18} />
          <span>{t('navFaq')}</span>
        </button>
      </div>

      {/* Tab Panels */}
      {activeTab === 'chat' && <ChatTabPanel />}
      {activeTab === 'search' && <SearchTabPanel initialQuery={searchParams.get('search') || ''} />}
      {activeTab === 'discovery' && <DiscoveryTabPanel />}
      {activeTab === 'faq' && <FaqTabPanel />}
    </div>
  );
}

/* 1. CHAT TAB PANEL */
function ChatTabPanel() {
  const { t } = useLanguage();
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: 'Namaste! I am the **BIS Intelligent Assistant**. How can I help you regarding Indian Standards, IS codes, or product compliance today?',
      citations: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [isVoiceOpen, setIsVoiceOpen] = useState(false);
  const [isCameraOpen, setIsCameraOpen] = useState(false);

  const handleSend = async (textToSend) => {
    const query = textToSend || inputQuery;
    if (!query.trim() || isLoading) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputQuery('');
    setIsLoading(true);

    try {
      const res = await sendChatMessage(query);
      const botMsg = {
        id: Date.now() + 1,
        sender: 'bot',
        text: res.data.answer,
        confidenceScore: res.data.confidenceScore,
        confidenceLabel: res.data.confidenceLabel,
        citations: res.data.citations || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'bot',
          text: 'Unable to reach the assistant at the moment. Please check network connection.',
          citations: [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleClear = () => {
    setMessages([
      {
        id: 1,
        sender: 'bot',
        text: 'Conversation cleared. Ask me another question about Indian Standards or BIS services.',
        citations: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  return (
    <div className="chat-tab-container">
      <div className="chat-header-toolbar">
        <span className="chat-status-text">
          <ShieldCheck size={16} className="text-success" />
          {t('ragGuardrailed')} Active
        </span>
        <Button variant="ghost" size="sm" icon={Trash2} onClick={handleClear}>
          {t('clearChatBtn')}
        </Button>
      </div>

      {/* Suggested Questions */}
      <div className="suggested-questions-row">
        <span className="suggested-label">{t('suggestedQueriesLabel')}</span>
        <div className="suggested-chips">
          {MOCK_SUGGESTED_QUESTIONS.map((q, idx) => (
            <button key={idx} type="button" className="suggested-chip" onClick={() => handleSend(q)}>
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Messages Stream */}
      <div className="messages-box">
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-bubble-wrapper ${msg.sender}`}>
            <div className="chat-avatar">
              {msg.sender === 'bot' ? <Bot size={20} /> : 'YOU'}
            </div>

            <div className="chat-bubble-content">
              <div className="bubble-header">
                <span className="bubble-author">{msg.sender === 'bot' ? t('appTitle') : 'User'}</span>
                <span className="bubble-time">{msg.timestamp}</span>
              </div>

              <div className="bubble-text">{msg.text}</div>

              {/* RAG Citations */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="citations-list">
                  {msg.citations.map((c, cIdx) => (
                    <RAGCitationCard
                      key={cIdx}
                      citation={c}
                      confidenceScore={msg.confidenceScore}
                      confidenceLabel={msg.confidenceLabel}
                    />
                  ))}
                </div>
              )}

              {msg.sender === 'bot' && (
                <div className="bubble-footer">
                  <button
                    type="button"
                    className="bubble-action-btn"
                    onClick={() => handleCopy(msg.id, msg.text)}
                  >
                    {copiedId === msg.id ? <Check size={14} color="#16a34a" /> : <Copy size={14} />}
                    <span>{copiedId === msg.id ? t('copiedBtn') : t('copyAnswerBtn')}</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="chat-bubble-wrapper bot">
            <div className="chat-avatar"><Bot size={20} /></div>
            <div className="chat-bubble-content">
              <LoadingState message="Searching official BIS repository & retrieving verified citations..." />
            </div>
          </div>
        )}
      </div>

      {/* Input Dock */}
      <div className="chat-input-dock">
        <div className="input-toolbar-left">
          <button type="button" className="input-tool-btn" onClick={() => setIsVoiceOpen(true)} title="Voice Input">
            <Mic size={18} />
          </button>
          <button type="button" className="input-tool-btn" onClick={() => setIsCameraOpen(true)} title="Camera Snapshot">
            <Camera size={18} />
          </button>
        </div>

        <input
          type="text"
          className="chat-text-input"
          placeholder={t('searchPlaceholder')}
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />

        <Button
          variant="primary"
          icon={Send}
          onClick={() => handleSend()}
          disabled={!inputQuery.trim() || isLoading}
        >
          {t('sendBtn')}
        </Button>
      </div>

      <VoiceInputModal
        isOpen={isVoiceOpen}
        onClose={() => setIsVoiceOpen(false)}
        onTranscriptSubmit={(tText) => { setInputQuery(tText); handleSend(tText); }}
      />

      <CameraCaptureModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onImageCaptured={(img) => {
          handleSend('Uploaded image for ISI mark compliance verification.');
        }}
      />
    </div>
  );
}

/* 2. SEARCH TAB PANEL */
function SearchTabPanel({ initialQuery }) {
  const { t } = useLanguage();
  const [query, setQuery] = useState(initialQuery || '');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [mandatoryOnly, setMandatoryOnly] = useState(false);
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedStandard, setSelectedStandard] = useState(null);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const res = await searchStandards(query, selectedCategory);
        let list = res.data;
        if (mandatoryOnly) {
          list = list.filter((s) => s.mandatory);
        }
        setResults(list);
      } catch (e) {
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, [query, selectedCategory, mandatoryOnly]);

  return (
    <div className="search-tab-container">
      <div className="search-controls-card">
        <div className="search-row">
          <SearchInput
            value={query}
            onChange={setQuery}
            placeholder={t('searchPlaceholder')}
            size="lg"
          />
        </div>

        <div className="filters-row">
          <div className="filter-group">
            <label className="filter-label">{t('filterCategory')}</label>
            <select
              className="filter-select"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              {CATEGORIES.map((cat, idx) => (
                <option key={idx} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <label className="mandatory-checkbox-label">
            <input
              type="checkbox"
              checked={mandatoryOnly}
              onChange={(e) => setMandatoryOnly(e.target.checked)}
            />
            <span>{t('mandatoryOnlyCheck')}</span>
          </label>
        </div>
      </div>

      {isLoading ? (
        <LoadingState message="Searching Indian Standards Directory..." />
      ) : results.length === 0 ? (
        <EmptyState
          title="No Indian Standards found"
          description={`No results matching "${query}". Try broadening your search or removing category filters.`}
        />
      ) : (
        <div className="standards-grid">
          {results.map((st) => (
            <Card key={st.id} hoverable className="standard-card">
              <div className="standard-card-header">
                <span className="standard-code">{st.code}</span>
                <Badge variant={st.mandatory ? 'error' : 'neutral'}>
                  {st.mandatory ? 'Mandatory ISI' : 'Voluntary'}
                </Badge>
              </div>

              <h4 className="standard-title">{st.title}</h4>
              <p className="standard-desc">{st.description}</p>

              <div className="standard-meta">
                <span className="meta-tag">{st.category}</span>
                <span className="meta-dept">{st.department}</span>
              </div>

              <div className="standard-card-footer">
                <Button variant="outline" size="sm" onClick={() => setSelectedStandard(st)}>
                  {t('viewParametersBtn')}
                </Button>
                {st.officialUrl && (
                  <a href={st.officialUrl} target="_blank" rel="noopener noreferrer" className="pdf-link-btn">
                    <ExternalLink size={14} /> PDF
                  </a>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Standard Details Modal */}
      {selectedStandard && (
        <div className="modal-backdrop" onClick={() => setSelectedStandard(null)}>
          <div className="modal-content standard-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3 className="modal-title">{selectedStandard.code}</h3>
                <span className="modal-subtitle-text">{selectedStandard.title}</span>
              </div>
              <button type="button" className="modal-close-btn" onClick={() => setSelectedStandard(null)}>✕</button>
            </div>

            <div className="modal-body">
              <div className="detail-section">
                <h5 className="section-heading">Key Technical Parameters & Limits:</h5>
                <table className="parameters-table">
                  <thead>
                    <tr>
                      <th>Parameter</th>
                      <th>Permissible Limit</th>
                      <th>Unit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedStandard.keyParameters.map((kp, idx) => (
                      <tr key={idx}>
                        <td><strong>{kp.parameter}</strong></td>
                        <td>{kp.limit}</td>
                        <td>{kp.unit}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="detail-section">
                <h5 className="section-heading">Certification Scheme:</h5>
                <p>{selectedStandard.compulsoryScheme}</p>
              </div>
            </div>

            <div className="modal-footer">
              <Button variant="outline" onClick={() => setSelectedStandard(null)}>Close</Button>
              {selectedStandard.officialUrl && (
                <a href={selectedStandard.officialUrl} target="_blank" rel="noopener noreferrer" className="btn btn-primary btn-md">
                  Download Official Standard PDF
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* 3. DISCOVERY TAB PANEL */
function DiscoveryTabPanel() {
  const [step, setStep] = useState(1);
  const [productType, setProductType] = useState('');
  const [material, setMaterial] = useState('');
  const [market, setMarket] = useState('');
  const [recommendation, setRecommendation] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    const res = await recommendStandards({ productType, material, market });
    setRecommendation(res.data);
    setIsAnalyzing(false);
    setStep(4);
  };

  return (
    <div className="discovery-tab-container">
      <Card title="AI Discovery Interview Wizard" subtitle="Answer 3 quick questions to discover applicable mandatory & voluntary Indian Standards for your product.">
        {step === 1 && (
          <div className="wizard-step">
            <h4 className="step-title">Step 1: Select Product Category</h4>
            <div className="option-grid">
              {['Packaged Drinking Water', 'Electrical Wires & Cables', 'Ceramic Tiles & Sanitaryware', 'Solar PV Modules & Inverters', 'LED Lighting & Drivers'].map((opt, idx) => (
                <button
                  key={idx}
                  type="button"
                  className={`wizard-option-card ${productType === opt ? 'selected' : ''}`}
                  onClick={() => setProductType(opt)}
                >
                  {opt}
                </button>
              ))}
            </div>
            <div className="wizard-footer">
              <Button variant="primary" disabled={!productType} onClick={() => setStep(2)}>Next Step →</Button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="wizard-step">
            <h4 className="step-title">Step 2: Core Material / Technology</h4>
            <div className="option-grid">
              {['Polyvinyl Chloride (PVC)', 'Polyethylene Terephthalate (PET)', 'Glazed Porcelain / Vitrified', 'Silicon Monocrystalline', 'Semiconductor Driver'].map((opt, idx) => (
                <button
                  key={idx}
                  type="button"
                  className={`wizard-option-card ${material === opt ? 'selected' : ''}`}
                  onClick={() => setMaterial(opt)}
                >
                  {opt}
                </button>
              ))}
            </div>
            <div className="wizard-footer">
              <Button variant="outline" onClick={() => setStep(1)}>← Back</Button>
              <Button variant="primary" disabled={!material} onClick={() => setStep(3)}>Next Step →</Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="wizard-step">
            <h4 className="step-title">Step 3: Target Commercial Market</h4>
            <div className="option-grid">
              {['Domestic Indian Retail Market', 'Government / Public Sector Procurement', 'Export & International Distribution'].map((opt, idx) => (
                <button
                  key={idx}
                  type="button"
                  className={`wizard-option-card ${market === opt ? 'selected' : ''}`}
                  onClick={() => setMarket(opt)}
                >
                  {opt}
                </button>
              ))}
            </div>
            <div className="wizard-footer">
              <Button variant="outline" onClick={() => setStep(2)}>← Back</Button>
              <Button variant="primary" icon={Sparkles} disabled={!market || isAnalyzing} onClick={handleAnalyze}>
                Run AI Standard Matcher
              </Button>
            </div>
          </div>
        )}

        {step === 4 && recommendation && (
          <div className="wizard-results">
            <Badge variant="success" dot className="mb-2">AI Match Complete</Badge>
            <h4 className="results-heading">Recommended Compliance Standards:</h4>
            <p className="summary-text">{recommendation.recommendationSummary}</p>

            <div className="recommended-list">
              <h5 className="list-title">Mandatory Standards (ISI / CRS Scheme):</h5>
              {recommendation.mandatory.map((st) => (
                <div key={st.id} className="rec-item">
                  <span className="rec-code">{st.code}</span>
                  <span className="rec-title">{st.title}</span>
                  <Badge variant="error" size="sm">Mandatory</Badge>
                </div>
              ))}
            </div>

            <Button variant="outline" onClick={() => setStep(1)} className="mt-4">
              Restart Discovery Wizard
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
}

/* 4. FAQ TAB PANEL */
function FaqTabPanel() {
  const [openIdx, setOpenIdx] = useState(null);

  const FAQS = [
    { q: 'What is an IS Code and how is it formulated by BIS?', a: 'An Indian Standard (IS Code) is a published technical specification formulated by sectional committees under BIS representing industry experts, government bodies, consumer groups, and testing laboratories.' },
    { q: 'What is the difference between ISI Mark (Scheme-I) and CRS Registration?', a: 'ISI Mark (Scheme-I) involves factory inspection, sample testing, and ongoing surveillance audits. CRS (Compulsory Registration Scheme) relies on self-declaration of conformity based on lab test reports for electronics and IT goods.' },
    { q: 'How can a consumer check if a product ISI mark is authentic?', a: 'Check for the 7-to-10 digit CML licence number printed directly under the ISI mark emblem. Enter this CML number into the VERIFY tab on this portal to see verified factory address and validity.' }
  ];

  return (
    <div className="faq-tab-container">
      <Card title="Trustworthy BIS Regulatory FAQ Directory">
        <div className="faq-accordion">
          {FAQS.map((faq, idx) => (
            <div key={idx} className="faq-item">
              <button
                type="button"
                className="faq-question-btn"
                onClick={() => setOpenIdx(openIdx === idx ? null : idx)}
              >
                <span>{faq.q}</span>
                {openIdx === idx ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </button>
              {openIdx === idx && (
                <div className="faq-answer-box">
                  <p>{faq.a}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

export default KnowPage;
