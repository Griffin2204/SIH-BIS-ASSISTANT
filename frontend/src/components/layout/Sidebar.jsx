import React from 'react';
import './Sidebar.css';
import { NavLink } from 'react-router-dom';
import { useLanguage } from '../../context/LanguageContext';
import {
  LayoutDashboard,
  Bot,
  FileSearch,
  CheckCircle2,
  FileText,
  MessageSquare,
  HelpCircle,
  X,
  Compass,
  ShieldAlert,
  Search,
  Sparkles,
  Award,
  Upload,
  UserCheck,
  Building2
} from 'lucide-react';

export function Sidebar({ isOpen, onClose }) {
  const { t } = useLanguage();

  const NAV_GROUPS = [
    {
      groupTitle: 'PORTAL HUB',
      items: [
        { path: '/', labelKey: 'navOverview', icon: LayoutDashboard }
      ]
    },
    {
      groupTitle: '1. KNOW MODE',
      items: [
        { path: '/know/chat', labelKey: 'navAskAi', icon: Bot, badge: 'RAG' },
        { path: '/know/search', labelKey: 'navSmartSearch', icon: FileSearch },
        { path: '/know/discovery', labelKey: 'navDiscovery', icon: Sparkles },
        { path: '/know/faq', labelKey: 'navFaq', icon: Compass }
      ]
    },
    {
      groupTitle: '2. COMPLY MODE',
      items: [
        { path: '/comply/dashboard', labelKey: 'navProducerDash', icon: Building2 },
        { path: '/comply/analyzer', labelKey: 'navProductAnalyzer', icon: Search },
        { path: '/comply/prefill', labelKey: 'navFormPrefill', icon: FileText },
        { path: '/comply/tracker', labelKey: 'navCertTracker', icon: Award }
      ]
    },
    {
      groupTitle: '3. VERIFY MODE',
      items: [
        { path: '/verify/dashboard', labelKey: 'navConsumerDash', icon: UserCheck },
        { path: '/verify/licence', labelKey: 'navCmlVerifier', icon: CheckCircle2 },
        { path: '/verify/huid', labelKey: 'navHuidCheck', icon: Award },
        { path: '/verify/fake-detector', labelKey: 'navFakeDetector', icon: ShieldAlert }
      ]
    },
    {
      groupTitle: 'DOCUMENTS & UTILITIES',
      items: [
        { path: '/documents', labelKey: 'navDocUpload', icon: Upload },
        { path: '/feedback', labelKey: 'navFeedback', icon: MessageSquare }
      ]
    }
  ];

  return (
    <>
      {isOpen && <div className="sidebar-backdrop" onClick={onClose} aria-hidden="true" />}

      <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <span className="sidebar-section-title">PORTAL NAVIGATION</span>
          <button type="button" className="sidebar-close-btn" onClick={onClose} aria-label="Close sidebar">
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {NAV_GROUPS.map((group, gIdx) => (
            <div key={gIdx} className="sidebar-group">
              <span className="sidebar-group-label">{group.groupTitle}</span>
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
                    }
                    onClick={onClose}
                  >
                    <Icon className="sidebar-link-icon" size={18} />
                    <span className="sidebar-link-label">{t(item.labelKey)}</span>
                    {item.badge && <span className="sidebar-link-badge">{item.badge}</span>}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-help-card">
            <HelpCircle size={20} className="help-icon" />
            <div className="help-text">
              <span className="help-title">National Standards</span>
              <span className="help-desc">AI Assistant Platform</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
