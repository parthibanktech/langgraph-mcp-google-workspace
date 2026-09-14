import React, { useEffect, useState } from 'react';
import { 
  Mail, 
  HardDrive, 
  Bot, 
  ShieldCheck, 
  ArrowUpRight, 
  Zap, 
  Clock, 
  CheckCircle2, 
  AlertTriangle 
} from 'lucide-react';

export default function DashboardView({ setActiveTab }) {
  const [stats, setStats] = useState({
    emails: 12,
    driveFiles: 45,
    agentQueries: 8,
    auditEvents: 24,
    rateLimitRemaining: '98/100'
  });

  const [recentLogs, setRecentLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/logs');
      if (res.ok) {
        const data = await res.json();
        if (data.logs) {
          setRecentLogs(data.logs.slice(0, 5));
        }
      }
    } catch (err) {
      console.warn("Could not fetch audit logs:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Top Metrics Cards */}
      <div className="grid-stats">
        <div className="card stat-card">
          <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818CF8' }}>
            <Mail size={24} />
          </div>
          <div>
            <div className="stat-value">{stats.emails}</div>
            <div className="stat-label">Gmail Messages Managed</div>
          </div>
        </div>

        <div className="card stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34D399' }}>
            <HardDrive size={24} />
          </div>
          <div>
            <div className="stat-value">{stats.driveFiles}</div>
            <div className="stat-label">Drive Files Indexed</div>
          </div>
        </div>

        <div className="card stat-card">
          <div className="stat-icon" style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#C084FC' }}>
            <Bot size={24} />
          </div>
          <div>
            <div className="stat-value">{stats.agentQueries}</div>
            <div className="stat-label">LangGraph Agent Calls</div>
          </div>
        </div>

        <div className="card stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#FBBF24' }}>
            <ShieldCheck size={24} />
          </div>
          <div>
            <div className="stat-value">{stats.rateLimitRemaining}</div>
            <div className="stat-label">Rate Limit Budget (Req/Min)</div>
          </div>
        </div>
      </div>

      {/* Quick Access Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column', justify: 'space-between' }}>
          <div>
            <div className="card-title" style={{ color: '#818CF8' }}>
              <Mail size={20} /> Gmail Inbox & Operations
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Search unread emails, read message bodies, inspect headers, or compose and dispatch emails via Google APIs.
            </p>
          </div>
          <button className="btn btn-secondary" onClick={() => setActiveTab('gmail')} style={{ alignSelf: 'flex-start' }}>
            Open Gmail Suite <ArrowUpRight size={16} />
          </button>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', justify: 'space-between' }}>
          <div>
            <div className="card-title" style={{ color: '#34D399' }}>
              <HardDrive size={20} /> Google Drive Explorer
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              List documents, search across Google Drive files by keyword, or retrieve detailed metadata and download links.
            </p>
          </div>
          <button className="btn btn-secondary" onClick={() => setActiveTab('drive')} style={{ alignSelf: 'flex-start' }}>
            Open Drive Explorer <ArrowUpRight size={16} />
          </button>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', justify: 'space-between' }}>
          <div>
            <div className="card-title" style={{ color: '#C084FC' }}>
              <Bot size={20} /> AI Agent Playground
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Interactive natural language chat powered by LangGraph to orchestrate email & drive actions automatically.
            </p>
          </div>
          <button className="btn btn-primary" onClick={() => setActiveTab('agent')} style={{ alignSelf: 'flex-start' }}>
            Launch AI Chat <Zap size={16} />
          </button>
        </div>
      </div>

      {/* Recent Security & Audit Logs */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div className="card-title" style={{ margin: 0 }}>
            <Clock size={20} /> Recent System Audit Activity
          </div>
          <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.75rem' }} onClick={fetchLogs}>
            Refresh Activity
          </button>
        </div>

        {recentLogs.length === 0 ? (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No recent audit log records loaded. Ensure backend is running.
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>User / Session</th>
                  <th>Action</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentLogs.map((log, idx) => (
                  <tr key={idx}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                      {log.timestamp || new Date().toISOString()}
                    </td>
                    <td>{log.user_id || 'system-user'}</td>
                    <td>
                      <span className="badge badge-indigo">
                        {log.action || log.raw || 'Tool Invocation'}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-emerald">
                        <CheckCircle2 size={12} /> Executed
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
