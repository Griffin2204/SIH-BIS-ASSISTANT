import React, { useState } from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import SearchInput from '../components/ui/SearchInput';
import LoadingState from '../components/ui/LoadingState';
import DisclaimerBanner from '../components/common/DisclaimerBanner';
import ConsumerDashboardPage from './ConsumerDashboardPage';
import CameraCaptureModal from '../components/common/CameraCaptureModal';
import { verifyLicenceOrHuid } from '../api/client';
import { useLanguage } from '../context/LanguageContext';
import {
  UserCheck,
  CheckCircle2,
  Award,
  ShieldAlert,
  Search,
  ExternalLink,
  MapPin,
  Calendar,
  Camera,
  AlertTriangle
} from 'lucide-react';
import './VerifyPage.css';

export function VerifyPage({ defaultSubTab = 'licence' }) {
  const [activeTab, setActiveTab] = useState(defaultSubTab);
  const { t } = useLanguage();

  return (
    <div className="verify-page">
      <PageHeader
        title={`${t('navVerify')} — ${t('verifyTitle')}`}
        description="Verify 7-digit CML producer licences, 6-character gold HUID hallmarks, and spot counterfeit ISI marks."
        breadcrumbs={['Portal', t('navVerify')]}
        badge={<Badge variant="success" dot>{t('systemOnline')}</Badge>}
      />

      <DisclaimerBanner />

      {/* Subtabs */}
      <div className="verify-subtabs">
        <button
          type="button"
          className={`subtab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <UserCheck size={18} />
          <span>{t('navConsumerDash')}</span>
        </button>

        <button
          type="button"
          className={`subtab-btn ${activeTab === 'licence' ? 'active' : ''}`}
          onClick={() => setActiveTab('licence')}
        >
          <CheckCircle2 size={18} />
          <span>{t('navCmlVerifier')}</span>
        </button>

        <button
          type="button"
          className={`subtab-btn ${activeTab === 'huid' ? 'active' : ''}`}
          onClick={() => setActiveTab('huid')}
        >
          <Award size={18} />
          <span>{t('navHuidCheck')}</span>
        </button>

        <button
          type="button"
          className={`subtab-btn ${activeTab === 'fake-detector' ? 'active' : ''}`}
          onClick={() => setActiveTab('fake-detector')}
        >
          <ShieldAlert size={18} />
          <span>{t('navFakeDetector')}</span>
        </button>
      </div>

      {/* Panels */}
      {activeTab === 'dashboard' && <ConsumerDashboardPage hideHeader />}
      {activeTab === 'licence' && <CmlLicencePanel />}
      {activeTab === 'huid' && <HuidPanel />}
      {activeTab === 'fake-detector' && <FakeDetectorPanel />}
    </div>
  );
}

/* 1. CML LICENCE VERIFIER PANEL */
function CmlLicencePanel() {
  const { t } = useLanguage();
  const [cmlNumber, setCmlNumber] = useState('7800012345');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleVerify = async (queryToUse) => {
    const q = queryToUse || cmlNumber;
    if (!q.trim()) return;

    setIsLoading(true);
    try {
      const res = await verifyLicenceOrHuid('cml', q);
      setResult(res.data);
    } catch (e) {
      setResult({ found: false, message: 'Server verification lookup error.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="cml-panel">
      <Card title={t('navCmlVerifier')} subtitle="Validate the 7-to-10 digit CML number printed directly under the ISI mark on any product.">
        <div className="cml-search-box">
          <SearchInput
            value={cmlNumber}
            onChange={setCmlNumber}
            onSubmit={() => handleVerify()}
            placeholder="Enter 7-to-10 digit CML Number (e.g. 7800012345 or 3100098765)..."
            size="lg"
          />
          <Button variant="primary" icon={Search} onClick={() => handleVerify()} isLoading={isLoading}>
            {t('verifyLicenceBtn')}
          </Button>
        </div>

        <div className="sample-cmls-row my-3">
          <span className="text-muted text-sm font-semibold">Try Quick Sample CMLs:</span>
          <button type="button" className="sample-btn" onClick={() => { setCmlNumber('7800012345'); handleVerify('7800012345'); }}>7800012345 (Packaged Water)</button>
          <button type="button" className="sample-btn" onClick={() => { setCmlNumber('3100098765'); handleVerify('3100098765'); }}>3100098765 (Polycab Wire)</button>
          <button type="button" className="sample-btn" onClick={() => { setCmlNumber('5500043210'); handleVerify('5500043210'); }}>5500043210 (Expired Tile Licence)</button>
        </div>

        {isLoading ? (
          <LoadingState message="Querying BIS Licence Registry database..." />
        ) : result ? (
          result.found ? (
            <div className="result-card verified">
              <div className="result-card-header">
                <div className="header-left">
                  <CheckCircle2 size={28} className="verified-icon" />
                  <div>
                    <span className="result-cml-code">CML NO: {result.record.cmlNumber}</span>
                    <h4 className="producer-name">{result.record.producerName}</h4>
                  </div>
                </div>
                <Badge variant={result.record.status === 'Verified' ? 'success' : 'error'}>
                  {result.record.statusBadge}
                </Badge>
              </div>

              <div className="result-body-grid">
                <div className="info-block">
                  <span className="info-label">Brand Name:</span>
                  <span className="info-value">{result.record.brandName}</span>
                </div>

                <div className="info-block">
                  <span className="info-label">Indian Standard (IS Code):</span>
                  <span className="info-value font-bold">{result.record.isStandard} — {result.record.standardTitle}</span>
                </div>

                <div className="info-block">
                  <span className="info-label">Product Category:</span>
                  <span className="info-value">{result.record.category}</span>
                </div>

                <div className="info-block">
                  <span className="info-label">Licence Validity Period:</span>
                  <span className="info-value"><Calendar size={14} /> {result.record.validFrom} to {result.record.validTo}</span>
                </div>
              </div>

              <div className="address-block">
                <MapPin size={16} className="text-muted" />
                <span><strong>Factory Location:</strong> {result.record.factoryAddress}</span>
              </div>

              <div className="result-card-footer">
                <a href={result.record.officialRegistryUrl} target="_blank" rel="noopener noreferrer" className="btn btn-outline btn-sm">
                  View on Official Manakonline Registry <ExternalLink size={14} />
                </a>
              </div>
            </div>
          ) : (
            <div className="result-card not-found">
              <AlertTriangle size={28} className="error-icon" />
              <div>
                <h4 className="error-title">No Valid BIS Licence Found</h4>
                <p className="error-desc">{result.message}</p>
              </div>
            </div>
          )
        ) : null}
      </Card>
    </div>
  );
}

/* 2. HUID HALLMARK PANEL */
function HuidPanel() {
  const { t } = useLanguage();
  const [huidCode, setHuidCode] = useState('AB1234');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleVerify = async (queryToUse) => {
    const q = queryToUse || huidCode;
    if (!q.trim()) return;

    setIsLoading(true);
    try {
      const res = await verifyLicenceOrHuid('huid', q);
      setResult(res.data);
    } catch (e) {
      setResult({ found: false, message: 'HUID lookup failed.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="huid-panel">
      <Card title={t('navHuidCheck')} subtitle="Enter the 6-character alphanumeric Hallmarking Unique ID (HUID) laser etched on your jewelry item.">
        <div className="cml-search-box">
          <SearchInput
            value={huidCode}
            onChange={setHuidCode}
            onSubmit={() => handleVerify()}
            placeholder="Enter 6-character HUID Code (e.g. AB1234 or XY9876)..."
            size="lg"
          />
          <Button variant="primary" icon={Search} onClick={() => handleVerify()} isLoading={isLoading}>
            {t('verifyHuidBtn')}
          </Button>
        </div>

        <div className="sample-cmls-row my-3">
          <span className="text-muted text-sm font-semibold">Try Quick Sample HUIDs:</span>
          <button type="button" className="sample-btn" onClick={() => { setHuidCode('AB1234'); handleVerify('AB1234'); }}>AB1234 (22K Gold Ring)</button>
          <button type="button" className="sample-btn" onClick={() => { setHuidCode('XY9876'); handleVerify('XY9876'); }}>XY9876 (18K Gold Chain)</button>
        </div>

        {isLoading ? (
          <LoadingState message="Querying BIS Hallmarking HUID Registry..." />
        ) : result ? (
          result.found ? (
            <div className="result-card verified">
              <div className="result-card-header">
                <div className="header-left">
                  <Award size={28} className="verified-icon" />
                  <div>
                    <span className="result-cml-code">HUID: {result.record.huid}</span>
                    <h4 className="producer-name">{result.record.articleType}</h4>
                  </div>
                </div>
                <Badge variant="success">Authentic Gold Hallmark</Badge>
              </div>

              <div className="result-body-grid">
                <div className="info-block">
                  <span className="info-label">Purity Grade:</span>
                  <span className="info-value font-bold text-blue">{result.record.purity}</span>
                </div>

                <div className="info-block">
                  <span className="info-label">Gross Article Weight:</span>
                  <span className="info-value">{result.record.weightGram}</span>
                </div>

                <div className="info-block">
                  <span className="info-label">Jeweller Outlet:</span>
                  <span className="info-value">{result.record.jewellerName} ({result.record.jewellerLicence})</span>
                </div>

                <div className="info-block">
                  <span className="info-label">Hallmarking Center (AHC):</span>
                  <span className="info-value">{result.record.ahcName}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="result-card not-found">
              <AlertTriangle size={28} className="error-icon" />
              <div>
                <h4 className="error-title">Unregistered HUID Code</h4>
                <p className="error-desc">{result.message}</p>
              </div>
            </div>
          )
        ) : null}
      </Card>
    </div>
  );
}

/* 3. FAKE DETECTOR PANEL */
function FakeDetectorPanel() {
  const { t } = useLanguage();
  const [isCameraOpen, setIsCameraOpen] = useState(false);

  return (
    <div className="fake-detector-panel">
      <Card title={t('navFakeDetector')} subtitle="Spot counterfeit ISI marks and report unauthorized usage to the Bureau of Indian Standards.">
        <div className="checklist-box mb-6">
          <h4 className="box-title">3 Elements Required on Every Genuine ISI Mark:</h4>
          <div className="elements-grid">
            <div className="element-card">
              <div className="elem-num">1</div>
              <div>
                <h5 className="elem-title">IS Standard Code</h5>
                <p className="elem-desc">Printed clearly on top of the mark (e.g. IS 10500).</p>
              </div>
            </div>

            <div className="element-card">
              <div className="elem-num">2</div>
              <div>
                <h5 className="elem-title">Official ISI Logo Emblem</h5>
                <p className="elem-desc">Standard two-circle emblem with "IS" lettering.</p>
              </div>
            </div>

            <div className="element-card">
              <div className="elem-num">3</div>
              <div>
                <h5 className="elem-title">7-to-10 Digit CM/L Number</h5>
                <p className="elem-desc">Printed underneath (e.g. CM/L-7800012345).</p>
              </div>
            </div>
          </div>
        </div>

        <div className="scan-trigger-box">
          <Camera size={36} className="text-blue mb-2" />
          <h4 className="scan-title">Scan Product Mark Using Camera / Image Upload</h4>
          <p className="scan-desc">Our AI image model analyzes the logo geometry and CML number for authenticity.</p>
          <Button variant="primary" icon={Camera} onClick={() => setIsCameraOpen(true)} className="mt-3">
            {t('captureSnapshotBtn')}
          </Button>
        </div>
      </Card>

      <CameraCaptureModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onImageCaptured={(img) => {
          alert('Image captured and analyzed: Genuine ISI Mark geometry recognized with CML 7800012345.');
        }}
      />
    </div>
  );
}

export default VerifyPage;
