import React, { useState, useEffect } from 'react';
import { 
  HardDrive, 
  Search, 
  FileText, 
  Folder, 
  FileSpreadsheet, 
  FileCode, 
  ExternalLink, 
  RefreshCw, 
  Eye, 
  X, 
  AlertCircle 
} from 'lucide-react';

export default function DriveView() {
  const [files, setFiles] = useState([]);
  const [keyword, setKeyword] = useState('');
  const [fileType, setFileType] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // File metadata inspect modal
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetchDriveFiles();
  }, []);

  const fetchDriveFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      let endpoint = '/api/drive/files';
      let bodyData = { query: keyword, max_results: 15, file_type: fileType };

      if (keyword.trim()) {
        endpoint = '/api/drive/search';
        bodyData = { keyword: keyword.trim(), max_results: 15 };
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyData)
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
      const fileList = Array.isArray(data.data) ? data.data : (data.data?.files || []);

      if (isOk) {
        setFiles(fileList);
      } else {
        setError(data.error || data.message || 'No Drive files retrieved');
        setFiles([]);
      }
    } catch (err) {
      setError('Backend connection error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = (mimeType = '') => {
    if (mimeType.includes('folder')) return <Folder size={18} style={{ color: '#FBBF24' }} />;
    if (mimeType.includes('spreadsheet') || mimeType.includes('sheet')) return <FileSpreadsheet size={18} style={{ color: '#34D399' }} />;
    if (mimeType.includes('document')) return <FileText size={18} style={{ color: '#818CF8' }} />;
    return <FileCode size={18} style={{ color: '#06B6D4' }} />;
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
                placeholder="Search Google Drive by file name or keyword..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && fetchDriveFiles()}
              />
            </div>
            <button className="btn btn-secondary" onClick={fetchDriveFiles} disabled={loading}>
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} /> Search
            </button>
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => { setFileType(''); fetchDriveFiles(); }}
              className={`badge ${fileType === '' ? 'badge-indigo' : 'badge-amber'}`}
              style={{ cursor: 'pointer', border: 'none' }}
            >
              All Types
            </button>
            <button
              onClick={() => { setFileType('application/vnd.google-apps.document'); fetchDriveFiles(); }}
              className={`badge ${fileType.includes('document') ? 'badge-indigo' : 'badge-amber'}`}
              style={{ cursor: 'pointer', border: 'none' }}
            >
              Docs
            </button>
            <button
              onClick={() => { setFileType('application/vnd.google-apps.folder'); fetchDriveFiles(); }}
              className={`badge ${fileType.includes('folder') ? 'badge-indigo' : 'badge-amber'}`}
              style={{ cursor: 'pointer', border: 'none' }}
            >
              Folders
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

      {/* Files Grid / Table */}
      <div className="card">
        <div className="card-title">
          <HardDrive size={20} style={{ color: '#34D399' }} /> Google Drive Files ({files.length})
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Retrieving Google Drive files...
          </div>
        ) : files.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No Google Drive files found.
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>MIME Type</th>
                  <th>File ID</th>
                  <th>Size</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {files.map((file) => (
                  <tr key={file.id}>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '10px' }}>
                      {getFileIcon(file.mimeType)}
                      <span>{file.name || 'Untitled File'}</span>
                    </td>
                    <td>
                      <span className="badge badge-indigo" style={{ fontSize: '0.7rem' }}>
                        {file.mimeType ? file.mimeType.split('.').pop() : 'file'}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
                      {file.id}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {file.size ? `${(file.size / 1024).toFixed(1)} KB` : 'N/A'}
                    </td>
                    <td>
                      <button 
                        className="btn btn-secondary" 
                        style={{ padding: '6px 10px', fontSize: '0.75rem' }}
                        onClick={() => setSelectedFile(file)}
                      >
                        <Eye size={14} /> Metadata
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* File Details Inspect Modal */}
      {selectedFile && (
        <div className="modal-overlay" onClick={() => setSelectedFile(null)}>
          <div className="modal-content animate-fade-in" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                {getFileIcon(selectedFile.mimeType)} {selectedFile.name}
              </h3>
              <button onClick={() => setSelectedFile(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '0.9rem' }}>
              <div><strong>File ID:</strong> <code style={{ background: 'var(--bg-input)', padding: '2px 6px', borderRadius: '4px' }}>{selectedFile.id}</code></div>
              <div><strong>MIME Type:</strong> {selectedFile.mimeType || 'Unknown'}</div>
              <div><strong>Modified Date:</strong> {selectedFile.modifiedTime || 'N/A'}</div>
              {selectedFile.webViewLink && (
                <div style={{ marginTop: '12px' }}>
                  <a href={selectedFile.webViewLink} target="_blank" rel="noreferrer" className="btn btn-primary">
                    Open in Google Drive <ExternalLink size={16} />
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
