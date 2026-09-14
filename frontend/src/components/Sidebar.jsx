import React from 'react';
import { 
  LayoutDashboard, 
  Mail, 
  HardDrive, 
  Bot, 
  Activity, 
  ShieldCheck, 
  Cpu 
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'gmail', label: 'Gmail Assistant', icon: Mail },
    { id: 'drive', label: 'Google Drive', icon: HardDrive },
    { id: 'agent', label: 'AI Agent Hub', icon: Bot },
    { id: 'api-monitor', label: 'API & Security Monitor', icon: Activity },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-badge">
          <Cpu size={22} />
        </div>
        <div>
          <div className="brand-title">Gmail & Drive MCP</div>
          <div className="brand-subtitle">LangGraph Agent Workspace</div>
        </div>
      </div>

      <nav className="nav-group">
        <div className="nav-label">Navigation</div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="server-status-card">
          <div className="status-indicator">
            <span className="dot-online"></span>
            <span>FastAPI Server</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Port: 8000 | MCP Connected
          </div>
        </div>
      </div>
    </aside>
  );
}
