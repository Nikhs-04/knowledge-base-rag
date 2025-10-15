import { useState, useEffect } from 'react';
import { Upload, Search, FileText, Database, Trash2, Loader } from 'lucide-react';
import './App.css';

export default function KnowledgeBaseApp() {
  const [files, setFiles] = useState([]);
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'; 

  useEffect(() => {
    fetchStats();
  }, []);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const uploadDocuments = async () => {
    if (files.length === 0) {
      alert('Please select files to upload');
      return;
    }

    setLoading(true);
    setUploadStatus('Uploading and processing documents...');

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus(`✓ Successfully processed ${result.statistics.documents} documents (${result.statistics.chunks} chunks)`);
        setFiles([]);
        document.getElementById('file-upload').value = '';
        fetchStats();
      } else {
        setUploadStatus(`✗ Error: ${result.detail}`);
      }
    } catch (error) {
      setUploadStatus(`✗ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const searchKnowledgeBase = async () => {
    if (!query.trim()) {
      alert('Please enter a question');
      return;
    }

    setLoading(true);
    setAnswer(null);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: query,
          top_k: 5,
          include_sources: true,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        setAnswer(result);
      } else {
        setAnswer({
          answer: `Error: ${result.detail}`,
          sources: [],
        });
      }
    } catch (error) {
      setAnswer({
        answer: `Error: ${error.message}`,
        sources: [],
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/stats`);
      const result = await response.json();
      setStats(result);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const clearKnowledgeBase = async () => {
    if (!window.confirm('Are you sure you want to clear all documents?')) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/clear`, {
        method: 'DELETE',
      });

      const result = await response.json();

      if (response.ok) {
        setUploadStatus('✓ Knowledge base cleared');
        setStats(null);
        setAnswer(null);
      } else {
        setUploadStatus(`✗ Error: ${result.detail}`);
      }
    } catch (error) {
      setUploadStatus(`✗ Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="main-content">
        {/* Header */}
        <div className="header">
          <h1>🔍 Knowledge Base Search Engine</h1>
          <p>Upload documents and search with AI-powered RAG using Ollama</p>
        </div>

        {/* Stats Bar */}
        {stats && stats.total_chunks > 0 && (
          <div className="stats-bar">
            <div className="stats-items">
              <div className="stat-item">
                <FileText style={{ color: '#667eea' }} />
                <span className="stat-label">
                  Documents: <span className="stat-value">{stats.total_documents}</span>
                </span>
              </div>
              <div className="stat-item">
                <Database style={{ color: '#48bb78' }} />
                <span className="stat-label">
                  Chunks: <span className="stat-value">{stats.total_chunks}</span>
                </span>
              </div>
            </div>
            <button onClick={clearKnowledgeBase} className="btn btn-danger" disabled={loading}>
              <Trash2 />
              Clear All
            </button>
          </div>
        )}

        {/* Cards Grid */}
        <div className="cards-grid">
          {/* Upload Card */}
          <div className="card">
            <div className="card-header">
              <Upload style={{ color: '#667eea' }} />
              <h2>Upload Documents</h2>
            </div>

            <div className="upload-dropzone">
              <input
                type="file"
                multiple
                accept=".pdf,.txt,.docx,.pptx"
                onChange={handleFileChange}
                id="file-upload"
              />
              <label htmlFor="file-upload" style={{ cursor: 'pointer', display: 'block' }}>
                <Upload style={{ margin: '0 auto 1rem' }} />
                <div className="upload-dropzone-text">
                  Click to select files or drag and drop
                </div>
                <div className="upload-dropzone-hint">
                  PDF, TXT, DOCX, PPTX
                </div>
              </label>
            </div>

            {files.length > 0 && (
              <div className="selected-files">
                <span className="selected-files-label">Selected Files ({files.length}):</span>
                <div className="files-list">
                  {files.map((file, index) => (
                    <div key={index} className="file-item">
                      {file.name}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              onClick={uploadDocuments}
              disabled={loading || files.length === 0}
              className="btn btn-primary"
            >
              {loading ? (
                <>
                  <Loader className="animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload />
                  Upload & Process
                </>
              )}
            </button>

            {uploadStatus && (
              <div className="status-message">
                {uploadStatus}
              </div>
            )}
          </div>

          {/* Search Card */}
          <div className="card">
            <div className="card-header">
              <Search style={{ color: '#48bb78' }} />
              <h2>Search Knowledge Base</h2>
            </div>

            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="search-textarea"
              rows="5"
            />

            <button
              onClick={searchKnowledgeBase}
              disabled={loading || !query.trim()}
              className="btn btn-success"
            >
              {loading ? (
                <>
                  <Loader className="animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search />
                  Search
                </>
              )}
            </button>
          </div>
        </div>

        {/* Answer Section */}
        {answer && (
          <div className="answer-card">
            <h2>💡 Answer</h2>

            <div className="answer-content">
              <p className="answer-text">{answer.answer}</p>
            </div>

            {answer.sources && answer.sources.length > 0 && (
              <div className="sources-section">
                <h3 className="sources-title">📚 Sources:</h3>
                <div className="sources-list">
                  {answer.sources.map((source, index) => (
                    <div key={index} className="source-item">
                      <div className="source-info">
                        <FileText />
                        <span className="source-name">{source.filename}</span>
                      </div>
                      <span className="source-score">
                        Score: {(source.relevance_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {answer.confidence && (
              <div className="confidence-badge">
                Confidence: 
                <span className={`confidence-value confidence-${answer.confidence}`}>
                  {' '}{answer.confidence}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}