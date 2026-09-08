import React from 'react';
import './Sidebar.css';
import { NavLink } from 'react-router-dom';
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
  Building2,
  History
} from 'lucide-react';

export const NAV_GROUPS = [
  {
    groupTitle: 'PORTAL HUB',
    items: [
      { path: '/', label: 'Overview Dashboard', icon: LayoutDashboard }
    ]
  },
  {
    groupTitle: '1. KNOW MODE',
    items: [
      { path: '/know/chat', label: 'Ask AI Assistant', icon: Bot, badge: 'RAG' },
      { path: '/know/search', label: 'Smart Standards Search', icon: FileSearch },
      { path: '/know/discovery', label: 'AI Discovery Interview', icon: Sparkles },
      { path: '/know/faq', label: 'Trustworthy FAQ', icon: Compass }
    ]
  },
  {
    groupTitle: '2. COMPLY MODE',
    items: [
      { path: '/comply/dashboard', label: 'Producer Dashboard', icon: Building2 },
      { path: '/comply/analyzer', label: 'Product Specs Analyzer', icon: Search },
      { path: '/comply/prefill', label: 'Form Pre-fill Assistant', icon: FileText },
      { path: '/comply/tracker', label: 'Certification Tracker', icon: Award }
    ]
  },
  {
    groupTitle: '3. VERIFY MODE',
    items: [
      { path: '/verify/dashboard', label: 'Consumer Dashboard', icon: UserCheck },
      { path: '/verify/licence', label: 'BIS CML Licence Verifier', icon: CheckCircle2 },
      { path: '/verify/huid', label: 'HUID Gold Hallmark Check', icon: Award },
      { path: '/verify/fake-detector', label: 'Fake Mark Detector', icon: ShieldAlert }
    ]
  },
  {
    groupTitle: 'DOCUMENTS & UTILITIES',
    items: [
      { path: '/documents', label: 'Document Upload & OCR', icon: Upload },
      { path: '/feedback', label: 'Feedback & Support', icon: MessageSquare }
    ]
  }
];

export function Sidebar({ isOpen, onClose }) {
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
                    <span className="sidebar-link-label">{item.label}</span>
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
              <span className="help-title">SIH 2026 Portal</span>
              <span className="help-desc">Team: localhost:8008</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
