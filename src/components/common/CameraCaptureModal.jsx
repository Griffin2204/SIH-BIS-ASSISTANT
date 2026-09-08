import React, { useState } from 'react';
import './CameraCaptureModal.css';
import { Camera, X, CheckCircle2, RefreshCw, Upload, Image as ImageIcon } from 'lucide-react';
import Button from '../ui/Button';

export function CameraCaptureModal({ isOpen, onClose, onImageCaptured }) {
  const [capturedImage, setCapturedImage] = useState(null);
  const [isCapturing, setIsCapturing] = useState(false);

  if (!isOpen) return null;

  const handleSimulateCapture = () => {
    setIsCapturing(true);
    setTimeout(() => {
      // Demo product mark image placeholder
      setCapturedImage('https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60');
      setIsCapturing(false);
    }, 1000);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const url = URL.createObjectURL(file);
      setCapturedImage(url);
    }
  };

  const handleRetake = () => {
    setCapturedImage(null);
  };

  const handleSubmit = () => {
    if (capturedImage && onImageCaptured) {
      onImageCaptured(capturedImage);
      onClose();
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content camera-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Camera & ISI Mark Scanner</h3>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="camera-modal-body">
          {!capturedImage ? (
            <div className="viewfinder-box">
              <div className="viewfinder-overlay">
                <div className="corner top-left" />
                <div className="corner top-right" />
                <div className="corner bottom-left" />
                <div className="corner bottom-right" />
                <span className="viewfinder-hint">Align ISI Mark or HUID Code within frame</span>
              </div>
              {isCapturing ? (
                <div className="capturing-loader">Capturing Snapshot...</div>
              ) : (
                <div className="viewfinder-placeholder">
                  <Camera size={48} className="camera-icon" />
                  <p>Live Camera Stream</p>
                </div>
              )}
            </div>
          ) : (
            <div className="preview-image-box">
              <img src={capturedImage} alt="Captured product mark" className="captured-img" />
              <span className="preview-badge">Snapshot Ready</span>
            </div>
          )}

          <div className="camera-actions-row">
            {!capturedImage ? (
              <>
                <Button variant="primary" icon={Camera} onClick={handleSimulateCapture} isLoading={isCapturing}>
                  Capture Snapshot
                </Button>
                <label className="btn btn-outline btn-md upload-label">
                  <Upload size={16} />
                  <span>Upload Image</span>
                  <input type="file" accept="image/*" onChange={handleFileChange} hidden />
                </label>
              </>
            ) : (
              <Button variant="outline" icon={RefreshCw} onClick={handleRetake}>
                Retake Photo
              </Button>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            icon={CheckCircle2}
            disabled={!capturedImage}
            onClick={handleSubmit}
          >
            Analyze Image
          </Button>
        </div>
      </div>
    </div>
  );
}

export default CameraCaptureModal;
