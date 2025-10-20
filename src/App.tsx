import React, { useState } from 'react';
import NotepadEditor from './components/NotepadEditor';
import Settings from './components/Settings';
import './App.css';

const App: React.FC = () => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  return (
    <div className="app">
      <div className="app-header">
        <h1>Pensieve AI</h1>
        <button 
          className="settings-button"
          onClick={() => setIsSettingsOpen(true)}
          title="Settings"
        >
          ⚙️
        </button>
      </div>
      <NotepadEditor />
      <Settings 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </div>
  );
};

export default App;
