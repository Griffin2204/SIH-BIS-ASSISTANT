import React from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import { Bot } from 'lucide-react';

export function AIAssistantPage() {
  return (
    <div>
      <PageHeader
        title="AI Assistant"
        description="Interactive AI assistant for BIS standards, compliance regulations, and technical queries."
        breadcrumbs={['Portal', 'AI Assistant']}
        badge={<Badge variant="blue">RAG Powered</Badge>}
      />
      <Card title="BIS Technical Assistant Chat">
        <p style={{ color: 'var(--text-secondary)' }}>AI Chat interface component placeholder.</p>
      </Card>
    </div>
  );
}

export default AIAssistantPage;
