import React, { useState, useEffect } from 'react';
import './VoiceInputModal.css';
import { Mic, MicOff, X, CheckCircle2, Volume2 } from 'lucide-react';
import Button from '../ui/Button';

export function VoiceInputModal({ isOpen, onClose, onTranscriptSubmit }) {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');

  useEffect(() => {
    let timer;
    if (isRecording) {
      setTranscript('Listening in Hindi / English...');
      timer = setTimeout(() => {
        setTranscript('What are the permissible TDS and lead limits for drinking water under IS 10500?');
      }, 1800);
    }
    return () => clearTimeout(timer);
  }, [isRecording]);

  if (!isOpen) return null;

  const handleStartRecording = () => {
    setIsRecording(true);
  };

  const handleStopRecording = () => {
    setIsRecording(false);
  };

  const handleSubmit = () => {
    if (transcript && onTranscriptSubmit) {
      onTranscriptSubmit(transcript);
      onClose();
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content voice-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">Voice Assistant Input</h3>
          <button type="button" className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="voice-modal-body">
          <div className={`mic-ring ${isRecording ? 'mic-active' : ''}`}>
            <button
              type="button"
              className={`mic-button ${isRecording ? 'recording' : ''}`}
              onClick={isRecording ? handleStopRecording : handleStartRecording}
            >
              <Mic size={36} />
            </button>
          </div>

          <p className="voice-status-text">
            {isRecording ? 'Listening... Speak your query clearly' : 'Tap microphone to start voice input'}
          </p>

          {isRecording && (
            <div className="soundwave-bar">
              <span /><span /><span /><span /><span />
            </div>
          )}

          <div className="transcript-box">
            <span className="transcript-label">Live Transcript Preview:</span>
            <p className="transcript-text">{transcript || 'No audio detected yet...'}</p>
          </div>
        </div>

        <div className="modal-footer">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            icon={CheckCircle2}
            disabled={!transcript || isRecording}
            onClick={handleSubmit}
          >
            Use Transcript
          </Button>
        </div>
      </div>
    </div>
  );
}

export default VoiceInputModal;
