import React from 'react';
import { Sun, Moon, Search, ShieldAlert, Sparkles } from 'lucide-react';

export default function Header({ activeTab, theme, toggleTheme }) {
  const getTabTitle = () => {
    switch (activeTab) {
      case 'dashboard': return 'Dashboard Overview -V2';
      case 'gmail': return 'Gmail Inbox & Assistant';
      case 'drive': return 'Google Drive File Explorer';
      case 'agent': return 'LangGraph AI Agent Playground';
      case 'api-monitor': return 'API & Audit Security Center';
      default: return 'Workspace';
    }
  };

  return (
    <header className="top-header">
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <h1 className="page-heading">{getTabTitle()}</h1>
        <span className="badge badge-indigo">
          <Sparkles size={12} /> MCP v1.0.0
        </span>
      </div>

      <div className="header-actions">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-emerald">
            Audit Security Active
          </span>
        </div>

        <button 
          onClick={toggleTheme} 
          className="theme-toggle-btn"
          title="Toggle Light/Dark Theme"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
