import React, { useState } from 'react';
import PageHeader from '../components/layout/PageHeader';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingState from '../components/ui/LoadingState';
import DisclaimerBanner from '../components/common/DisclaimerBanner';
import { uploadDocument } from '../api/client';
import {
  Upload,
  FileText,
  Trash2,
  CheckCircle2,
  FileCheck,
  AlertCircle,
  Eye,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import './DocumentsPage.css';

export function DocumentsPage() {
  const [dragOver, setDragOver] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState([
    {
      fileId: 'DOC-101',
      filename: 'Water_Quality_Test_Report_2026.pdf',
      fileSizeFormatted: '2.45 MB',
      status: 'Extracted & Analyzed',
      extractedText: 'SAMPLE OCR EXTRACT: Product: Packaged Mineral Water. pH: 7.2, TDS: 310 mg/l, Lead: 0.002 mg/l. Conforms to IS 10500:2012 specification.',
      identifiedStandard: 'IS 10500:2012',
      confidenceScore: '98.2%',
      suggestedActions: ['Apply for SIT Endorsement', 'Schedule Audit']
    }
  ]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const files = e.dataTransfer.files;
    if (files.length > 0) processFile(files[0]);
  };

  const handleFileSelect = (e) => {
    const files = e.target.files;
    if (files.length > 0) processFile(files[0]);
  };

  const processFile = async (file) => {
    setIsUploading(true);
    setUploadProgress(20);

    const interval = setInterval(() => {
      setUploadProgress((prev) => (prev >= 90 ? 90 : prev + 25));
    }, 200);

    try {
      const res = await uploadDocument(file);
      clearInterval(interval);
      setUploadProgress(100);
      setTimeout(() => {
        setUploadedDocs((prev) => [res.data, ...prev]);
        setIsUploading(false);
        setUploadProgress(0);
      }, 400);
    } catch (err) {
      clearInterval(interval);
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDelete = (id) => {
    setUploadedDocs((prev) => prev.filter((d) => d.fileId !== id));
  };

  return (
    <div className="documents-page">
      <PageHeader
        title="Document Upload & Automated OCR Analysis"
        description="Upload test certificates, lab reports, and technical brochures for AI extraction and standard matching."
        breadcrumbs={['Portal', 'Documents']}
        badge={<Badge variant="info">OCR Engine Active</Badge>}
      />

      <DisclaimerBanner />

      <Card title="Upload PDF or Image Document" subtitle="Supports PDF, JPEG, PNG up to 15MB per file">
        <div
          className={`dropzone-area ${dragOver ? 'dragover' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          <Upload size={40} className="dropzone-icon" />
          <h4 className="dropzone-title">Drag & Drop Your Document Here</h4>
          <p className="dropzone-sub">or click below to browse files from your computer</p>

          <label className="btn btn-primary btn-md cursor-pointer mt-3">
            <span>Browse Computer Files</span>
            <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={handleFileSelect} hidden />
          </label>
        </div>

        {isUploading && (
          <div className="upload-progress-box my-4">
            <div className="progress-text-row mb-1">
              <span>Uploading & Processing Document...</span>
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
        <h3 className="section-title mb-3">Processed Documents ({uploadedDocs.length})</h3>

        {uploadedDocs.length === 0 ? (
          <p className="text-muted">No uploaded documents yet. Use the upload box above.</p>
        ) : (
          <div className="docs-list">
            {uploadedDocs.map((doc) => (
              <Card key={doc.fileId} className="doc-card mb-4">
                <div className="doc-card-header">
                  <div className="header-left">
                    <FileText size={28} className="text-blue" />
                    <div>
                      <h4 className="doc-filename">{doc.filename}</h4>
                      <span className="doc-size">{doc.fileSizeFormatted}</span>
                    </div>
                  </div>

                  <div className="header-right">
                    <Badge variant="success" dot>{doc.status}</Badge>
                    <Button variant="ghost" size="sm" icon={Trash2} onClick={() => handleDelete(doc.fileId)}>
                      Delete
                    </Button>
                  </div>
                </div>

                <div className="doc-body">
                  <div className="extracted-box mb-3">
                    <span className="box-label">Extracted OCR Metadata:</span>
                    <p className="extracted-text">{doc.extractedText}</p>
                  </div>

                  <div className="standard-match-badge-row">
                    <Sparkles size={16} className="text-blue" />
                    <span>Identified Matching Standard: <strong>{doc.identifiedStandard}</strong></span>
                    <Badge variant="blue" size="sm">Confidence {doc.confidenceScore}</Badge>
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
