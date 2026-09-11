import React, { useState } from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import DisclaimerBanner from '../components/common/DisclaimerBanner';
import ProducerDashboardPage from './ProducerDashboardPage';
import { MOCK_STANDARDS } from '../data/mockStandards';
import { useLanguage } from '../context/LanguageContext';
import {
  Building2,
  Search,
  FileText,
  Award,
  CheckCircle2,
  ArrowRight,
  FileCheck,
  Zap,
  Sliders
} from 'lucide-react';
import './ComplyPage.css';

export function ComplyPage({ defaultSubTab = 'dashboard' }) {
  const [activeTab, setActiveTab] = useState(defaultSubTab);
  const { t } = useLanguage();

  return (
    <div className="comply-page">
      <PageHeader
        title={`${t('navComply')} — ${t('complyTitle')}`}
        description="Streamline BIS ISI mark and CRS registration, test parameter compliance analysis, form pre-fill, and application tracking."
        breadcrumbs={['Portal', t('navComply')]}
        badge={<Badge variant="navy" dot>{t('navProducerDash')}</Badge>}
      />

      <DisclaimerBanner />

      {/* Subtabs */}
      <div className="comply-subtabs">
        <button
          type="button"
          className={`subtab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <Building2 size={18} />
          <span>{t('navProducerDash')}</span>
        </button>

        <button
          type="button"
          className={`subtab-btn ${activeTab === 'analyzer' ? 'active' : ''}`}
          onClick={() => setActiveTab('analyzer')}
        >
          <Search size={18} />
          <span>{t('navProductAnalyzer')}</span>
        </button>

        <button
          type="button"
          className={`subtab-btn ${activeTab === 'prefill' ? 'active' : ''}`}
          onClick={() => setActiveTab('prefill')}
        >
          <FileText size={18} />
          <span>{t('navFormPrefill')}</span>
        </button>

        <button
          type="button"
          className={`subtab-btn ${activeTab === 'tracker' ? 'active' : ''}`}
          onClick={() => setActiveTab('tracker')}
        >
          <Award size={18} />
          <span>{t('navCertTracker')}</span>
        </button>
      </div>

      {/* Panels */}
      {activeTab === 'dashboard' && <ProducerDashboardPage hideHeader />}
      {activeTab === 'analyzer' && <ProductAnalyzerPanel />}
      {activeTab === 'prefill' && <FormPrefillPanel />}
      {activeTab === 'tracker' && <CertificationTrackerPanel />}
    </div>
  );
}

/* 1. PRODUCT ANALYZER PANEL */
function ProductAnalyzerPanel() {
  const { t } = useLanguage();
  const [selectedStandard, setSelectedStandard] = useState(MOCK_STANDARDS[0]);
  const [inputTds, setInputTds] = useState('350');
  const [inputPh, setInputPh] = useState('7.4');
  const [inputLead, setInputLead] = useState('0.005');
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleRunAnalysis = () => {
    const tds = parseFloat(inputTds);
    const ph = parseFloat(inputPh);
    const lead = parseFloat(inputLead);

    const tdsPass = tds <= 500;
    const phPass = ph >= 6.5 && ph <= 8.5;
    const leadPass = lead <= 0.01;

    const overallPass = tdsPass && phPass && leadPass;

    setAnalysisResult({
      overallPass,
      parameters: [
        { name: 'pH Value', value: ph, limit: '6.5 to 8.5', pass: phPass },
        { name: 'TDS (Total Dissolved Solids)', value: `${tds} mg/l`, limit: '500 mg/l max', pass: tdsPass },
        { name: 'Lead Content (Pb)', value: `${lead} mg/l`, limit: '0.01 mg/l max', pass: leadPass }
      ]
    });
  };

  return (
    <div className="analyzer-panel">
      <Card title={t('navProductAnalyzer')} subtitle="Test your factory lab output parameters against mandatory IS specifications prior to official audit.">
        <div className="analyzer-form">
          <div className="form-group">
            <label className="form-label">Target Indian Standard:</label>
            <select
              className="form-select"
              value={selectedStandard.id}
              onChange={(e) => setSelectedStandard(MOCK_STANDARDS.find((s) => s.id === e.target.value))}
            >
              {MOCK_STANDARDS.map((s) => (
                <option key={s.id} value={s.id}>{s.code} - {s.title}</option>
              ))}
            </select>
          </div>

          <div className="inputs-grid">
            <div className="form-group">
              <label className="form-label">Lab Result: pH Value</label>
              <input type="number" step="0.1" className="form-input" value={inputPh} onChange={(e) => setInputPh(e.target.value)} />
            </div>

            <div className="form-group">
              <label className="form-label">Lab Result: TDS (mg/l)</label>
              <input type="number" className="form-input" value={inputTds} onChange={(e) => setInputTds(e.target.value)} />
            </div>

            <div className="form-group">
              <label className="form-label">Lab Result: Lead (mg/l)</label>
              <input type="number" step="0.001" className="form-input" value={inputLead} onChange={(e) => setInputLead(e.target.value)} />
            </div>
          </div>

          <Button variant="primary" icon={Zap} onClick={handleRunAnalysis}>
            {t('evaluateComplianceBtn')}
          </Button>
        </div>

        {analysisResult && (
          <div className="analysis-output">
            <div className={`status-banner ${analysisResult.overallPass ? 'pass' : 'fail'}`}>
              <CheckCircle2 size={24} />
              <div>
                <h4 className="banner-title">
                  {analysisResult.overallPass ? 'Compliance Ready — All Parameters Passed' : 'Compliance Warning — Parameters Exceed Limits'}
                </h4>
                <p className="banner-desc">
                  {analysisResult.overallPass
                    ? 'Your test outputs satisfy all mandatory threshold limits under IS 10500:2012.'
                    : 'One or more parameters exceed the permissible limits. Adjustment required before SIT submission.'}
                </p>
              </div>
            </div>

            <table className="analysis-table">
              <thead>
                <tr>
                  <th>Test Parameter</th>
                  <th>Your Measured Output</th>
                  <th>IS Permissible Limit</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {analysisResult.parameters.map((p, idx) => (
                  <tr key={idx}>
                    <td><strong>{p.name}</strong></td>
                    <td>{p.value}</td>
                    <td>{p.limit}</td>
                    <td>
                      <Badge variant={p.pass ? 'success' : 'error'} size="sm">
                        {p.pass ? 'PASS' : 'EXCEEDED'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}

/* 2. FORM PREFILL PANEL */
function FormPrefillPanel() {
  const { t } = useLanguage();
  const [formState, setFormState] = useState({
    companyName: 'AquaPure Bottlers India Pvt Ltd',
    factoryAddress: 'Plot 42, MIDC Chakan, Pune, Maharashtra',
    brandName: 'AquaPure Mineral',
    isStandard: 'IS 10500:2012',
    qcManager: 'Rajesh Kumar (M.Sc. Chemistry)'
  });
  const [isPrefilled, setIsPrefilled] = useState(false);

  const handlePrefillFromDoc = () => {
    setIsPrefilled(true);
  };

  return (
    <div className="prefill-panel">
      <Card title={t('navFormPrefill')} subtitle="Automatically populates official Manakonline application fields from uploaded test reports and GST certificates.">
        <div className="prefill-toolbar mb-4">
          <Button variant="secondary" icon={FileCheck} onClick={handlePrefillFromDoc}>
            {t('prefillDocBtn')}
          </Button>
          {isPrefilled && <Badge variant="success">Metadata Extracted (98% Accuracy)</Badge>}
        </div>

        <form className="prefill-form" onSubmit={(e) => e.preventDefault()}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Applicant Company Name:</label>
              <input type="text" className="form-input" value={formState.companyName} onChange={(e) => setFormState({ ...formState, companyName: e.target.value })} />
            </div>

            <div className="form-group">
              <label className="form-label">Brand / Trade Name:</label>
              <input type="text" className="form-input" value={formState.brandName} onChange={(e) => setFormState({ ...formState, brandName: e.target.value })} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Factory Manufacturing Address:</label>
            <input type="text" className="form-input" value={formState.factoryAddress} onChange={(e) => setFormState({ ...formState, factoryAddress: e.target.value })} />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Applied Indian Standard:</label>
              <input type="text" className="form-input" value={formState.isStandard} readOnly />
            </div>

            <div className="form-group">
              <label className="form-label">Quality Control Head:</label>
              <input type="text" className="form-input" value={formState.qcManager} onChange={(e) => setFormState({ ...formState, qcManager: e.target.value })} />
            </div>
          </div>

          <Button variant="primary" icon={ArrowRight}>
            Export Application Draft to Manakonline Portal
          </Button>
        </form>
      </Card>
    </div>
  );
}

/* 3. CERTIFICATION TRACKER PANEL */
function CertificationTrackerPanel() {
  const [labChoice, setLabChoice] = useState('NABL Accredited Central Lab');

  const STAGES = [
    { num: 1, title: 'Document & SIT Submission', status: 'Completed', date: '15 Jan 2026' },
    { num: 2, title: 'Factory Audit & Sample Sealing', status: 'Completed', date: '28 Jan 2026' },
    { num: 3, title: 'Independent NABL Laboratory Testing', status: 'In Progress', date: 'Est. 18 Mar 2026' },
    { num: 4, title: 'Grant of Licence (CML Number Generation)', status: 'Pending', date: 'Pending' }
  ];

  return (
    <div className="tracker-panel">
      <Card title="BIS Application Progress Tracker" subtitle="Live tracking of Application APP-2026-8891 for IS 10500:2012">
        <div className="tracker-timeline">
          {STAGES.map((stg) => (
            <div key={stg.num} className={`timeline-step ${stg.status.toLowerCase().replace(' ', '-')}`}>
              <div className="step-number">{stg.num}</div>
              <div className="step-info">
                <h5 className="step-title">{stg.title}</h5>
                <span className="step-date">{stg.date}</span>
              </div>
              <Badge variant={stg.status === 'Completed' ? 'success' : stg.status === 'In Progress' ? 'warning' : 'neutral'}>
                {stg.status}
              </Badge>
            </div>
          ))}
        </div>

        <div className="simulator-box mt-6">
          <div className="simulator-header">
            <Sliders size={20} className="text-blue" />
            <h4 className="simulator-title">What-If Compliance Simulator</h4>
          </div>

          <p className="simulator-desc">Test how changing testing labs or audit dates impacts your licence approval timeline:</p>

          <div className="form-group my-3">
            <label className="form-label">Selected Test Laboratory:</label>
            <select className="form-select" value={labChoice} onChange={(e) => setLabChoice(e.target.value)}>
              <option value="NABL Accredited Central Lab">NABL Accredited Central Lab (Fast-track 15 Days)</option>
              <option value="Regional Government Lab">Regional Government Lab (Standard 30 Days)</option>
            </select>
          </div>

          <div className="sim-result-badge">
            <CheckCircle2 size={16} /> Estimated CML Grant Date: <strong>{labChoice.includes('Fast-track') ? '25 March 2026' : '15 April 2026'}</strong>
          </div>
        </div>
      </Card>
    </div>
  );
}

export default ComplyPage;
