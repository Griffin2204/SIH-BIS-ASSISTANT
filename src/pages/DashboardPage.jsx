import React from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { Bot, FileSearch, CheckCircle2, FileText, ArrowRight, Activity, ShieldAlert, FileCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function DashboardPage() {
  const navigate = useNavigate();

  return (
    <div className="dashboard-page">
      <PageHeader
        title="BIS AI Assistant Dashboard"
        description="Bureau of Indian Standards intelligent compliance, verification, and technical assistance portal."
        breadcrumbs={['Portal', 'Dashboard']}
        badge={<Badge variant="success" dot>System Online</Badge>}
        actions={
          <Button variant="primary" icon={Bot} onClick={() => navigate('/chatbot')}>
            Launch AI Assistant
          </Button>
        }
      />

      {/* Quick Action Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
        <Card hoverable title="Ask AI Assistant" subtitle="Instant guidance on Indian Standards & IS codes">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1rem' }}>
            <Bot size={32} style={{ color: 'var(--blue-600)' }} />
            <Button variant="outline" size="sm" icon={ArrowRight} iconPosition="right" onClick={() => navigate('/chatbot')}>
              Start Chat
            </Button>
          </div>
        </Card>

        <Card hoverable title="Search BIS Standards" subtitle="Semantic search across technical documents">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1rem' }}>
            <FileSearch size={32} style={{ color: 'var(--navy-700)' }} />
            <Button variant="outline" size="sm" icon={ArrowRight} iconPosition="right" onClick={() => navigate('/standards')}>
              Search Standards
            </Button>
          </div>
        </Card>

        <Card hoverable title="Verify Credentials" subtitle="Validate CML numbers & ISI license status">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1rem' }}>
            <CheckCircle2 size={32} style={{ color: 'var(--color-success)' }} />
            <Button variant="outline" size="sm" icon={ArrowRight} iconPosition="right" onClick={() => navigate('/verification')}>
              Verify License
            </Button>
          </div>
        </Card>

        <Card hoverable title="Upload & Analyze" subtitle="Automated BIS document compliance check">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1rem' }}>
            <FileText size={32} style={{ color: 'var(--color-info)' }} />
            <Button variant="outline" size="sm" icon={ArrowRight} iconPosition="right" onClick={() => navigate('/documents')}>
              Upload Document
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default DashboardPage;
