import React from 'react';
import './TerminalHeader.css';

const TerminalHeader: React.FC = () => {
  return (
    <div className="terminal-header">
      <div className="terminal-controls">
        <div className="control-dot red"></div>
        <div className="control-dot yellow"></div>
        <div className="control-dot green"></div>
      </div>
      <div className="terminal-title">
        <span className="terminal-icon">⚡</span>
        Pensieve - IDE for Leaders
      </div>
      <div className="terminal-menu">
        <span className="menu-item">File</span>
        <span className="menu-item">Edit</span>
        <span className="menu-item">View</span>
        <span className="menu-item">Tools</span>
        <span className="menu-item">Help</span>
      </div>
    </div>
  );
};

export default TerminalHeader;
