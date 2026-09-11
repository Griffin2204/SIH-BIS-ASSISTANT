import React, { useState, useEffect, useCallback } from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingState from '../components/ui/LoadingState';
import DisclaimerBanner from '../components/common/DisclaimerBanner';
import { uploadDocument, getDocuments } from '../api/client';
import {
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import './DocumentsPage.css';

function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (_) {
    return dateStr;
  }
}

export function DocumentsPage() {
  const [dragOver, setDragOver] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [fetchError, setFetchError] = useState('');

  const fetchDocuments = useCallback(async () => {
    setIsLoadingDocs(true);
    setFetchError('');
    try {
      const res = await getDocuments();
      setUploadedDocs(res.data || []);
    } catch (err) {
      console.error('Failed to load documents from backend:', err);
      setFetchError(err.message || 'Unable to connect to document service.');
    } finally {
      setIsLoadingDocs(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) processFile(files[0]);
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFile(files[0]);
      e.target.value = '';
    }
  };

  const processFile = async (file) => {
    setUploadError('');
    setUploadSuccess('');

    if (!file) {
      setUploadError('Please select a file.');
      return;
    }
    if (file.size === 0) {
      setUploadError('Selected file is empty (0 bytes).');
      return;
    }
    if (file.size > 15 * 1024 * 1024) {
      setUploadError('File size exceeds the 15 MB limit.');
      return;
    }
    const ext = file.name ? file.name.slice(file.name.lastIndexOf('.')).toLowerCase() : '';
    const allowed = ['.pdf', '.docx', '.txt'];
    if (!allowed.includes(ext)) {
      setUploadError('Unsupported file type. Please upload a PDF, DOCX, or TXT file.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(15);

    const progressTimer = setInterval(() => {
      setUploadProgress((prev) => (prev >= 85 ? 85 : prev + 15));
    }, 250);

    try {
      const res = await uploadDocument(file);
      clearInterval(progressTimer);
      setUploadProgress(100);
      setUploadSuccess(`Successfully uploaded "${file.name}"! Indexed ${res.data.chunk_count} chunk(s) into vector store.`);
      await fetchDocuments();
      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress(0);
      }, 500);
    } catch (err) {
      clearInterval(progressTimer);
      setIsUploading(false);
      setUploadProgress(0);
      setUploadError(err.message || 'Failed to upload document.');
    }
  };

  return (
    <div className="documents-page">
      <PageHeader
        title="Document Upload & Vector Indexing"
        description="Upload test certificates, lab reports, and technical standards for automated text extraction, chunking, and semantic vector indexing."
        breadcrumbs={['Portal', 'Documents']}
        badge={<Badge variant="info">Vector Store Active</Badge>}
      />

      <DisclaimerBanner />

      <Card title="Upload Document" subtitle="Supports PDF, DOCX, and TXT up to 15 MB per file">
        <div
          className={`dropzone-area ${dragOver ? 'dragover' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          <Upload size={40} className="dropzone-icon" />
          <h4 className="dropzone-title">Drag & Drop Your Document Here</h4>
          <p className="dropzone-sub">Upload PDF, DOCX, or TXT documents to extract text and index into the assistant's knowledge base</p>

          <label className="btn btn-primary btn-md cursor-pointer mt-3">
            <span>Browse Computer Files</span>
            <input type="file" accept=".pdf,.docx,.txt" onChange={handleFileSelect} hidden />
          </label>
        </div>

        {uploadError && (
          <div className="alert alert-danger mt-3" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1rem', background: '#fee2e2', color: '#991b1b', borderRadius: 'var(--radius-md)', fontSize: '0.875rem' }}>
            <AlertCircle size={18} />
            <span>{uploadError}</span>
          </div>
        )}

        {uploadSuccess && (
          <div className="alert alert-success mt-3" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1rem', background: '#dcfce7', color: '#166534', borderRadius: 'var(--radius-md)', fontSize: '0.875rem' }}>
            <CheckCircle2 size={18} />
            <span>{uploadSuccess}</span>
          </div>
        )}

        {isUploading && (
          <div className="upload-progress-box my-4">
            <div className="progress-text-row mb-1">
              <span>Uploading, Processing & Indexing Document...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="progress-track">
              <div className="progress-fill" style={{ width: `${uploadProgress}%` }} />
            </div>
          </div>
        )}
      </Card>

      {/* Uploaded Documents List */}
      <div className="mt-6">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <h3 className="section-title" style={{ margin: 0 }}>
            Processed & Indexed Documents ({uploadedDocs.length})
          </h3>
          <Button
            variant="ghost"
            size="sm"
            icon={RefreshCw}
            onClick={fetchDocuments}
            disabled={isLoadingDocs}
          >
            {isLoadingDocs ? 'Refreshing...' : 'Refresh'}
          </Button>
        </div>

        {fetchError && (
          <div className="alert alert-warning mb-4" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1rem', background: '#fef3c7', color: '#92400e', borderRadius: 'var(--radius-md)', fontSize: '0.875rem' }}>
            <AlertCircle size={18} />
            <span>{fetchError}</span>
          </div>
        )}

        {isLoadingDocs && uploadedDocs.length === 0 ? (
          <LoadingState message="Loading documents from backend..." />
        ) : uploadedDocs.length === 0 ? (
          <p className="text-muted">No uploaded documents yet. Use the upload box above to index a PDF, DOCX, or TXT file into the assistant's knowledge base.</p>
        ) : (
          <div className="docs-list">
            {uploadedDocs.map((doc) => (
              <Card key={doc.document_id} className="doc-card mb-4">
                <div className="doc-card-header">
                  <div className="header-left">
                    <FileText size={28} className="text-blue" />
                    <div>
                      <h4 className="doc-filename">{doc.filename}</h4>
                      <span className="doc-size">
                        {formatFileSize(doc.file_size)} • {doc.file_type ? doc.file_type.toUpperCase() : 'DOC'}
                        {doc.pages ? ` • ${doc.pages} page${doc.pages > 1 ? 's' : ''}` : ''}
                        {doc.uploaded_at ? ` • ${formatDate(doc.uploaded_at)}` : ''}
                      </span>
                    </div>
                  </div>

                  <div className="header-right">
                    <Badge variant={doc.vector_store_status === 'indexed' ? 'success' : 'info'} dot>
                      {doc.vector_store_status === 'indexed' ? 'Indexed in Vector Store' : (doc.vector_store_status || 'Processed')}
                    </Badge>
                  </div>
                </div>

                <div className="doc-body">
                  <div className="extracted-box mb-3">
                    <span className="box-label">Extraction & Vectorization:</span>
                    <p className="extracted-text">
                      Extracted and cleaned {doc.cleaned_text_length || doc.text_length || 0} characters into {doc.chunk_count} semantic chunk(s).
                      Embedding model: <strong>{doc.embedding_model || 'all-MiniLM-L6-v2'}</strong> ({doc.embedding_dimension || 384} dimensions).
                    </p>
                  </div>

                  <div className="standard-match-badge-row">
                    <Sparkles size={16} className="text-blue" />
                    <span>Persisted in ChromaDB vector store. Available for semantic RAG retrieval in the BIS Assistant chat.</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default DocumentsPage;
