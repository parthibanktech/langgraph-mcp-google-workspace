import React, { useState, useEffect } from 'react';
import { 
  Mail, 
  Search, 
  Send, 
  RefreshCw, 
  Eye, 
  X, 
  User, 
  Calendar, 
  CheckCircle, 
  AlertCircle 
} from 'lucide-react';

export default function GmailView() {
  const [emails, setEmails] = useState([]);
  const [query, setQuery] = useState('is:unread');
  const [maxResults, setMaxResults] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Selected email reader modal
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [readingEmail, setReadingEmail] = useState(false);

  // Send Email Form Modal
  const [showSendModal, setShowSendModal] = useState(false);
  const [sendForm, setSendForm] = useState({ to: '', subject: '', body: '', cc: '', bcc: '' });
  const [sending, setSending] = useState(false);
  const [sendSuccess, setSendSuccess] = useState(null);

  useEffect(() => {
    fetchEmails();
  }, []);

  const fetchEmails = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/gmail/list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, max_results: parseInt(maxResults) })
      });
      if (!res.ok) {
        if (res.status === 502 || res.status === 504 || res.status === 500) {
          throw new Error(`Backend server offline or unreachable (HTTP ${res.status}). Please ensure 'python backend/api.py' is running on port 8000.`);
        }
        throw new Error(`HTTP ${res.status}: ${res.statusText || 'Server Error'}`);
      }
      const rawText = await res.text();
      let data;
      try {
        data = JSON.parse(rawText);
      } catch {
        throw new Error("Invalid or empty response received from API server.");
      }
      const isOk = data.success === true || data.status === 'success';
      const emailList = Array.isArray(data.data) ? data.data : (data.data?.emails || []);

      if (isOk) {
        setEmails(emailList);
      } else {
        setError(data.error || data.message || 'Failed to retrieve emails');
        setEmails([]);
      }
    } catch (err) {
      setError('Backend API error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const readFullEmail = async (emailId) => {
    setReadingEmail(true);
    try {
      const res = await fetch(`/api/gmail/read/${emailId}`);
      if (!res.ok) {
        if (res.status === 502 || res.status === 504 || res.status === 500) {
          throw new Error(`Backend server offline (HTTP ${res.status}). Please ensure 'python backend/api.py' is running.`);
        }
        throw new Error(`HTTP ${res.status}: ${res.statusText || 'Server Error'}`);
      }
      const rawText = await res.text();
      let data;
      try {
        data = JSON.parse(rawText);
      } catch {
        throw new Error("Invalid response format from server.");
      }
      const isOk = data.success === true || data.status === 'success';
      if (isOk && data.data) {
        setSelectedEmail(data.data);
      } else {
        setSelectedEmail({ id: emailId, body: data.error || 'Could not load content', subject: 'Error' });
      }
    } catch (err) {
      setSelectedEmail({ id: emailId, body: 'Error: ' + err.message });
    } finally {
      setReadingEmail(false);
    }
  };

  const handleSendEmail = async (e) => {
    e.preventDefault();
    setSending(true);
    setSendSuccess(null);
    try {
      const toList = sendForm.to.split(',').map(s => s.trim()).filter(Boolean);
      const ccList = sendForm.cc ? sendForm.cc.split(',').map(s => s.trim()).filter(Boolean) : null;
      const bccList = sendForm.bcc ? sendForm.bcc.split(',').map(s => s.trim()).filter(Boolean) : null;

      const res = await fetch('/api/gmail/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to: toList,
          subject: sendForm.subject,
          body: sendForm.body,
          cc: ccList,
          bcc: bccList
        })
      });
      if (!res.ok) {
        if (res.status === 502 || res.status === 504 || res.status === 500) {
          throw new Error(`Backend server offline (HTTP ${res.status}). Please ensure 'python backend/api.py' is running.`);
        }
        throw new Error(`HTTP ${res.status}: ${res.statusText || 'Server Error'}`);
      }
      const rawText = await res.text();
      let data;
      try {
        data = JSON.parse(rawText);
      } catch {
        throw new Error("Invalid response format from server.");
      }
      if (data.status === 'success' || data.success === true) {
        setSendSuccess('Email dispatched successfully! Message ID: ' + (data.data?.id || data.data?.message_id || 'N/A'));
        setSendForm({ to: '', subject: '', body: '', cc: '', bcc: '' });
        setTimeout(() => {
          setShowSendModal(false);
          setSendSuccess(null);
        }, 2000);
      } else {
        setError('Send Email Failed: ' + (data.message || data.error || 'Unknown error'));
      }
    } catch (err) {
      setError('Send Email Error: ' + err.message);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Control Header */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: '12px', flex: 1, minWidth: '280px' }}>
            <div className="search-box">
              <Search size={18} style={{ color: 'var(--text-muted)' }} />
              <input
                type="text"
                placeholder="Filter emails (e.g., is:unread, from:google)..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && fetchEmails()}
              />
            </div>
            <button className="btn btn-secondary" onClick={fetchEmails} disabled={loading}>
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
              Fetch
            </button>
          </div>

          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '6px' }}>
              {['is:unread', 'is:starred', 'label:INBOX'].map((badgeQuery) => (
                <button
                  key={badgeQuery}
                  onClick={() => { setQuery(badgeQuery); fetchEmails(); }}
                  className={`badge ${query === badgeQuery ? 'badge-indigo' : 'badge-amber'}`}
                  style={{ cursor: 'pointer', border: 'none' }}
                >
                  {badgeQuery}
                </button>
              ))}
            </div>

            <button className="btn btn-primary" onClick={() => setShowSendModal(true)}>
              <Send size={16} /> Compose Email
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="card" style={{ marginBottom: '20px', borderColor: 'var(--rose-accent)', background: 'rgba(239, 68, 68, 0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#F87171' }}>
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Email List Table */}
      <div className="card">
        <div className="card-title">
          <Mail size={20} style={{ color: '#818CF8' }} /> Inbox Email List ({emails.length})
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading emails from Gmail API...
          </div>
        ) : emails.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No emails found for query "{query}".
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Sender</th>
                  <th>Subject</th>
                  <th>Snippet / Body Preview</th>
                  <th>Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {emails.map((msg) => (
                  <tr key={msg.id || msg.threadId}>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                      {msg.from || msg.sender || 'Unknown Sender'}
                    </td>
                    <td style={{ fontWeight: 500 }}>
                      {msg.subject || '(No Subject)'}
                    </td>
                    <td style={{ maxWidth: '350px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {msg.snippet || msg.body || ''}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {msg.date || 'Recent'}
                    </td>
                    <td>
                      <button 
                        className="btn btn-secondary" 
                        style={{ padding: '6px 10px', fontSize: '0.75rem' }}
                        onClick={() => readFullEmail(msg.id)}
                      >
                        <Eye size={14} /> Read
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Email Content Reader Modal */}
      {selectedEmail && (
        <div className="modal-overlay" onClick={() => setSelectedEmail(null)}>
          <div className="modal-content animate-fade-in" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem' }}>
                {selectedEmail.subject || 'Email Details'}
              </h3>
              <button 
                onClick={() => setSelectedEmail(null)} 
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', gap: '16px', marginBottom: '16px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <div><User size={14} inline /> {selectedEmail.from || selectedEmail.sender}</div>
              <div><Calendar size={14} inline /> {selectedEmail.date || 'N/A'}</div>
            </div>

            <div style={{ 
              background: 'var(--bg-input)', 
              padding: '16px', 
              borderRadius: 'var(--radius-md)', 
              maxHeight: '350px', 
              overflowY: 'auto',
              whiteSpace: 'pre-wrap',
              fontSize: '0.9rem',
              lineHeight: '1.6'
            }}>
              {readingEmail ? 'Loading email content...' : (selectedEmail.body || selectedEmail.snippet || 'No message content')}
            </div>
          </div>
        </div>
      )}

      {/* Compose Send Email Modal */}
      {showSendModal && (
        <div className="modal-overlay" onClick={() => setShowSendModal(false)}>
          <div className="modal-content animate-fade-in" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Send size={18} style={{ color: 'var(--primary-accent)' }} /> Compose New Email
              </h3>
              <button onClick={() => setShowSendModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {sendSuccess && (
              <div style={{ padding: '12px', borderRadius: 'var(--radius-md)', background: 'rgba(16, 185, 129, 0.15)', color: '#34D399', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle size={18} /> {sendSuccess}
              </div>
            )}

            <form onSubmit={handleSendEmail}>
              <div className="form-group">
                <label className="form-label">To (comma separated):</label>
                <input
                  type="text"
                  required
                  placeholder="recipient@example.com"
                  className="form-input"
                  value={sendForm.to}
                  onChange={(e) => setSendForm({ ...sendForm, to: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Subject:</label>
                <input
                  type="text"
                  required
                  placeholder="Project Status Update"
                  className="form-input"
                  value={sendForm.subject}
                  onChange={(e) => setSendForm({ ...sendForm, subject: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Email Body Content:</label>
                <textarea
                  required
                  rows={6}
                  placeholder="Type your message content here..."
                  className="form-textarea"
                  value={sendForm.body}
                  onChange={(e) => setSendForm({ ...sendForm, body: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '20px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowSendModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={sending}>
                  {sending ? 'Sending...' : 'Send Message'} <Send size={16} />
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
