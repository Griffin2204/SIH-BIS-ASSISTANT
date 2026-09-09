import React from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import DisclaimerBanner from '../components/common/DisclaimerBanner';
import { useLanguage } from '../context/LanguageContext';
import {
  Bot,
  FileSearch,
  CheckCircle2,
  FileText,
  ShieldCheck,
  Award,
  Building2,
  UserCheck,
  Zap
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './DashboardPage.css';

export function DashboardPage() {
  const navigate = useNavigate();
  const { t } = useLanguage();

  return (
    <div className="dashboard-page">
      <PageHeader
        title={t('appTitle')}
        description="Intelligent Compliance, Verification, and Technical Assistance Framework for Indian Standards (IS Codes)."
        breadcrumbs={['Portal', t('navOverview')]}
        badge={<Badge variant="success" dot>{t('systemOnline')}</Badge>}
        actions={
          <Button variant="primary" icon={Bot} onClick={() => navigate('/know/chat')}>
            {t('launchAiBtn')}
          </Button>
        }
      />

      <DisclaimerBanner />

      {/* Quick Stats Banner */}
      <div className="portal-stats-grid mb-6">
        <Card className="portal-stat-card">
          <div className="stat-card-icon bg-blue-50 text-blue"><FileSearch size={22} /></div>
          <div>
            <span className="stat-num">24,500+</span>
            <span className="stat-name">{t('indexedStandards')}</span>
          </div>
        </Card>

        <Card className="portal-stat-card">
          <div className="stat-card-icon bg-green-50 text-success"><CheckCircle2 size={22} /></div>
          <div>
            <span className="stat-num">1,85,000+</span>
            <span className="stat-name">{t('activeLicences')}</span>
          </div>
        </Card>

        <Card className="portal-stat-card">
          <div className="stat-card-icon bg-amber-50 text-warning"><Award size={22} /></div>
          <div>
            <span className="stat-num">12.4 Crore</span>
            <span className="stat-name">{t('verifiedHuid')}</span>
          </div>
        </Card>

        <Card className="portal-stat-card">
          <div className="stat-card-icon bg-navy-50 text-navy"><ShieldCheck size={22} /></div>
          <div>
            <span className="stat-num">98.4%</span>
            <span className="stat-name">{t('confidenceRate')}</span>
          </div>
        </Card>
      </div>

      {/* Main Core Mode Launchpad */}
      <h3 className="section-title mb-3">{t('coreModesTitle')}</h3>
      <div className="modes-launchpad-grid mb-6">
        {/* KNOW MODE */}
        <Card hoverable className="mode-launch-card know-theme" onClick={() => navigate('/know')}>
          <div className="mode-card-header">
            <div className="mode-icon-box"><Bot size={24} /></div>
            <Badge variant="blue">1. {t('navKnow')}</Badge>
          </div>
          <h4 className="mode-card-title">{t('knowTitle')}</h4>
          <p className="mode-card-desc">{t('knowDesc')}</p>
          <div className="mode-card-footer">
            <span className="mode-link-text">{t('exploreKnow')}</span>
          </div>
        </Card>

        {/* COMPLY MODE */}
        <Card hoverable className="mode-launch-card comply-theme" onClick={() => navigate('/comply')}>
          <div className="mode-card-header">
            <div className="mode-icon-box"><Building2 size={24} /></div>
            <Badge variant="navy">2. {t('navComply')}</Badge>
          </div>
          <h4 className="mode-card-title">{t('complyTitle')}</h4>
          <p className="mode-card-desc">{t('complyDesc')}</p>
          <div className="mode-card-footer">
            <span className="mode-link-text">{t('exploreComply')}</span>
          </div>
        </Card>

        {/* VERIFY MODE */}
        <Card hoverable className="mode-launch-card verify-theme" onClick={() => navigate('/verify')}>
          <div className="mode-card-header">
            <div className="mode-icon-box"><UserCheck size={24} /></div>
            <Badge variant="success">3. {t('navVerify')}</Badge>
          </div>
          <h4 className="mode-card-title">{t('verifyTitle')}</h4>
          <p className="mode-card-desc">{t('verifyDesc')}</p>
          <div className="mode-card-footer">
            <span className="mode-link-text">{t('exploreVerify')}</span>
          </div>
        </Card>
      </div>

      {/* Feature Short-Cuts Grid */}
      <h3 className="section-title mb-3">{t('quickToolsTitle')}</h3>
      <div className="tools-grid mb-6">
        <Card hoverable className="tool-shortcut-card" onClick={() => navigate('/know/search')}>
          <FileSearch size={24} className="text-blue mb-2" />
          <h5 className="tool-name">{t('navSmartSearch')}</h5>
          <p className="tool-desc">Search IS 10500, IS 694, IS 13630 specifications & limits.</p>
        </Card>

        <Card hoverable className="tool-shortcut-card" onClick={() => navigate('/verify/licence')}>
          <CheckCircle2 size={24} className="text-success mb-2" />
          <h5 className="tool-name">{t('navCmlVerifier')}</h5>
          <p className="tool-desc">Verify 7-digit manufacturer ISI licence numbers.</p>
        </Card>

        <Card hoverable className="tool-shortcut-card" onClick={() => navigate('/verify/huid')}>
          <Award size={24} className="text-warning mb-2" />
          <h5 className="tool-name">{t('navHuidCheck')}</h5>
          <p className="tool-desc">Check 6-character gold hallmark authenticity.</p>
        </Card>

        <Card hoverable className="tool-shortcut-card" onClick={() => navigate('/documents')}>
          <FileText size={24} className="text-info mb-2" />
          <h5 className="tool-name">{t('navDocUpload')}</h5>
          <p className="tool-desc">Extract text & parameters from lab test PDFs.</p>
        </Card>
      </div>
    </div>
  );
}

export default DashboardPage;
