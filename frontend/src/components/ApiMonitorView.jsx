import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  ShieldCheck, 
  ExternalLink, 
  RefreshCw, 
  CheckCircle, 
  FileText, 
  Lock, 
  Server 
} from 'lucide-react';

export default function ApiMonitorView() {
  const [health, setHealth] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    checkHealth();
    fetchLogs();
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      } else {
        setHealth({ status: 'offline', service: `Server Error (${res.status})` });
      }
    } catch (err) {
      setHealth({ status: 'offline', service: 'FastAPI Backend Disconnected' });
    }
  };

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/logs');
      if (res.ok) {
        const rawText = await res.text();
        try {
          const data = JSON.parse(rawText);
          if (data.logs) {
            setLogs(data.logs);
          }
        } catch (e) {
          console.warn("Invalid log response format", e);
        }
      }
    } catch (err) {
      console.warn("Audit logs error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Top System Health Panel */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-title">
          <Server size={20} style={{ color: '#6366F1' }} /> System Architecture & API Health
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginTop: '16px' }}>
          <div style={{ background: 'var(--bg-input)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>FastAPI Server Status</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '6px' }}>
              <span className={`dot-online`} style={{ background: health?.status === 'healthy' ? 'var(--emerald-accent)' : 'var(--rose-accent)' }} />
              <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>
                {health ? health.status.toUpperCase() : 'CHECKING...'}
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Endpoint: http://localhost:8000/health
            </div>
          </div>

          <div style={{ background: 'var(--bg-input)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Interactive OpenAPI Documentation</div>
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
              <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                Swagger UI <ExternalLink size={14} />
              </a>
              <a href="http://localhost:8000/redoc" target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                ReDoc Spec <ExternalLink size={14} />
              </a>
            </div>
          </div>

          <div style={{ background: 'var(--bg-input)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Security Layer Enforcements</div>
            <div style={{ display: 'flex', gap: '6px', marginTop: '8px', flexWrap: 'wrap' }}>
              <span className="badge badge-emerald"><ShieldCheck size={12} /> Rate Limiter</span>
              <span className="badge badge-indigo"><Lock size={12} /> Input Validator</span>
              <span className="badge badge-amber"><FileText size={12} /> Audit Logger</span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Audit Log Activity Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div className="card-title" style={{ margin: 0 }}>
            <Activity size={20} style={{ color: '#FBBF24' }} /> Complete Security Audit Log Stream ({logs.length})
          </div>
          <button className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.75rem' }} onClick={fetchLogs} disabled={loading}>
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh Logs
          </button>
        </div>

        {logs.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No audit log entries recorded yet. Execute email or drive actions to trigger logs.
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Session ID / User</th>
                  <th>Action Executed</th>
                  <th>Details / Payload</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((item, idx) => (
                  <tr key={idx}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                      {item.timestamp || 'N/A'}
                    </td>
                    <td>{item.user_id || item.session_id || 'system-user'}</td>
                    <td>
                      <span className="badge badge-indigo">
                        {item.action || 'Tool Action'}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {JSON.stringify(item.details || item.raw || item)}
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
