import React, { useState } from 'react';
import './Navbar.css';
import { ShieldCheck, Menu, Bell, User, Mic, Camera } from 'lucide-react';
import SearchInput from '../ui/SearchInput';
import Badge from '../ui/Badge';
import MultilingualSelector from '../common/MultilingualSelector';
import VoiceInputModal from '../common/VoiceInputModal';
import CameraCaptureModal from '../common/CameraCaptureModal';
import { NavLink } from 'react-router-dom';

export function Navbar({ onMenuToggle, searchValue, onSearchChange, onSearchSubmit }) {
  const [isVoiceOpen, setIsVoiceOpen] = useState(false);
  const [isCameraOpen, setIsCameraOpen] = useState(false);

  const handleVoiceSubmit = (transcript) => {
    if (onSearchChange) onSearchChange(transcript);
    if (onSearchSubmit) onSearchSubmit(transcript);
  };

  const handleCameraCapture = (imgUrl) => {
    if (onSearchChange) onSearchChange('Uploaded ISI Mark Image for Analysis');
  };

  return (
    <>
      <header className="navbar">
        <div className="navbar-left">
          <button
            type="button"
            className="navbar-menu-btn"
            onClick={onMenuToggle}
            aria-label="Toggle navigation menu"
          >
            <Menu size={22} />
          </button>

          <NavLink to="/" className="navbar-brand">
            <div className="navbar-logo">
              <ShieldCheck size={24} color="#ffffff" />
            </div>
            <div className="navbar-title-group">
              <h1 className="navbar-title">BIS AI Assistant</h1>
              <span className="navbar-subtitle">GovTech Portal</span>
            </div>
          </NavLink>

          <nav className="mode-switcher-nav">
            <NavLink to="/know" className={({ isActive }) => `mode-pill ${isActive ? 'active' : ''}`}>
              KNOW
            </NavLink>
            <NavLink to="/comply" className={({ isActive }) => `mode-pill ${isActive ? 'active' : ''}`}>
              COMPLY
            </NavLink>
            <NavLink to="/verify" className={({ isActive }) => `mode-pill ${isActive ? 'active' : ''}`}>
              VERIFY
            </NavLink>
          </nav>
        </div>

        <div className="navbar-center">
          <SearchInput
            value={searchValue}
            onChange={onSearchChange}
            onSubmit={onSearchSubmit}
            placeholder="Search IS codes, CML licence, products..."
            size="sm"
          />
        </div>

        <div className="navbar-right">
          <div className="quick-input-tools">
            <button
              type="button"
              className="nav-tool-btn"
              onClick={() => setIsVoiceOpen(true)}
              title="Voice Query Input"
            >
              <Mic size={17} />
            </button>

            <button
              type="button"
              className="nav-tool-btn"
              onClick={() => setIsCameraOpen(true)}
              title="Camera / ISI Mark Scanner"
            >
              <Camera size={17} />
            </button>
          </div>

          <MultilingualSelector />

          <div className="user-profile">
            <div className="user-avatar">
              <User size={18} />
            </div>
            <div className="user-info">
              <span className="user-name">BIS Official</span>
              <span className="user-role">Government Admin</span>
            </div>
          </div>
        </div>
      </header>

      <VoiceInputModal
        isOpen={isVoiceOpen}
        onClose={() => setIsVoiceOpen(false)}
        onTranscriptSubmit={handleVoiceSubmit}
      />

      <CameraCaptureModal
        isOpen={isCameraOpen}
        onClose={() => setIsCameraOpen(false)}
        onImageCaptured={handleCameraCapture}
      />
    </>
  );
}

export default Navbar;
