import React from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { PRODUCER_DASHBOARD_DATA } from '../data/mockDashboards';
import { Building2, AlertTriangle, ArrowRight, CheckCircle2, Clock, Upload, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function ProducerDashboardPage({ hideHeader = false }) {
  const navigate = useNavigate();
  const { activeApplications, revisedStandardAlerts, complianceChecklist } = PRODUCER_DASHBOARD_DATA;

  return (
    <div className="producer-dashboard">
      {!hideHeader && (
        <PageHeader
          title="Producer & Manufacturer Compliance Hub"
          description="Manage active BIS licence applications, track SIT testing audits, and resolve revised standard alerts."
          breadcrumbs={['Portal', 'Producer Dashboard']}
          badge={<Badge variant="navy">Manufacturer Portal</Badge>}
        />
      )}

      {/* Overview Cards */}
      <div className="stats-row mb-6">
        <Card className="stat-card">
          <span className="stat-label">Active Applications</span>
          <span className="stat-value">2 Applications</span>
          <span className="stat-sub">1 In Progress, 1 Action Required</span>
        </Card>

        <Card className="stat-card">
          <span className="stat-label">Mandatory SIT Checklists</span>
          <span className="stat-value">80% Complete</span>
          <span className="stat-sub">4 of 5 requirements verified</span>
        </Card>

        <Card className="stat-card">
          <span className="stat-label">Revised Standard Alerts</span>
          <span className="stat-value text-warning">2 Alerts</span>
          <span className="stat-sub">Action required prior to next audit</span>
        </Card>
      </div>

      {/* Active Applications Section */}
      <div className="section-block mb-6">
        <h3 className="section-title mb-3">Active BIS Licence Applications</h3>
        <div className="apps-grid">
          {activeApplications.map((app) => (
            <Card key={app.id} hoverable className="app-card">
              <div className="app-card-header">
                <div>
                  <span className="app-id">{app.id}</span>
                  <h4 className="app-name">{app.productName}</h4>
                </div>
                <Badge variant={app.status === 'In Progress' ? 'warning' : 'error'}>
                  {app.status}
                </Badge>
              </div>

              <div className="app-progress-bar-wrapper my-2">
                <div className="progress-label-row">
                  <span>Stage: {app.currentStage}</span>
                  <span>{app.progressPercent}%</span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${app.progressPercent}%` }} />
                </div>
              </div>

              <p className="app-action-text"><strong>Next Step:</strong> {app.nextAction}</p>

              <div className="app-card-footer mt-3">
                <Button variant="outline" size="sm" icon={ArrowRight} iconPosition="right" onClick={() => navigate('/documents')}>
                  Upload Required Documents
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Revised Standard Alerts */}
      <div className="section-block mb-6">
        <h3 className="section-title mb-3">Revised Indian Standard Alerts (QCO Updates)</h3>
        <div className="alerts-list">
          {revisedStandardAlerts.map((alt) => (
            <div key={alt.id} className="alert-item-card">
              <div className="alert-icon"><AlertTriangle size={20} /></div>
              <div className="alert-body">
                <div className="alert-head">
                  <span className="alert-code">{alt.code}</span>
                  <span className="alert-date">Effective: {alt.effectiveDate}</span>
                </div>
                <p className="alert-title">{alt.title}</p>
                <p className="alert-req"><strong>Action Required:</strong> {alt.actionRequired}</p>
              </div>
              <Button variant="outline" size="sm" onClick={() => navigate('/know/search')}>
                View Amendment PDF
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ProducerDashboardPage;
