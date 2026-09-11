import React from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { CONSUMER_DASHBOARD_DATA } from '../data/mockDashboards';
import { UserCheck, History, Bookmark, ShieldAlert, CheckCircle2, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function ConsumerDashboardPage({ hideHeader = false }) {
  const navigate = useNavigate();
  const { recentVerifications, savedProducts, suspiciousReports } = CONSUMER_DASHBOARD_DATA;

  return (
    <div className="consumer-dashboard">
      {!hideHeader && (
        <PageHeader
          title="Consumer Verification & Protection Dashboard"
          description="Your personal activity log for ISI mark verifications, gold HUID checks, and saved product watches."
          breadcrumbs={['Portal', 'Consumer Dashboard']}
          badge={<Badge variant="success">Consumer Portal</Badge>}
        />
      )}

      {/* Quick Action Grid */}
      <div className="quick-actions-row mb-6">
        <Card hoverable className="action-card" onClick={() => navigate('/verify/licence')}>
          <CheckCircle2 size={28} className="text-blue mb-2" />
          <h4 className="card-heading">Verify ISI CML Licence</h4>
          <p className="card-sub">Check 7-digit CML number on bottled water, electrical wires, appliances.</p>
        </Card>

        <Card hoverable className="action-card" onClick={() => navigate('/verify/huid')}>
          <Badge variant="blue" className="mb-2">Gold & Silver</Badge>
          <h4 className="card-heading">Verify HUID Hallmark</h4>
          <p className="card-sub">Check 6-character code etched on gold jewelry articles.</p>
        </Card>

        <Card hoverable className="action-card" onClick={() => navigate('/verify/fake-detector')}>
          <ShieldAlert size={28} className="text-danger mb-2" />
          <h4 className="card-heading">Report Suspicious Mark</h4>
          <p className="card-sub">Report fake ISI marks or missing CML numbers directly to BIS enforcement.</p>
        </Card>
      </div>

      {/* Verification History Log */}
      <div className="section-block mb-6">
        <h3 className="section-title mb-3">Recent Verification History</h3>
        <Card padding="none">
          <div className="history-table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Query Code</th>
                  <th>Verified Result</th>
                  <th>Status</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {recentVerifications.map((item) => (
                  <tr key={item.id}>
                    <td><strong>{item.type}</strong></td>
                    <td className="code-cell">{item.query}</td>
                    <td>{item.resultName}</td>
                    <td>
                      <Badge variant={item.status.includes('Expired') ? 'error' : 'success'} size="sm">
                        {item.status}
                      </Badge>
                    </td>
                    <td className="text-muted">{item.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Saved Watchlist */}
      <div className="section-block">
        <h3 className="section-title mb-3">Saved Product Watchlist</h3>
        <div className="saved-products-grid">
          {savedProducts.map((p) => (
            <Card key={p.id} className="saved-card">
              <div className="saved-card-header">
                <span className="saved-code">{p.code}</span>
                <Badge variant="success" size="sm">{p.status}</Badge>
              </div>
              <h4 className="saved-title">{p.title}</h4>
              <span className="saved-cml">CML: {p.cml}</span>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ConsumerDashboardPage;
