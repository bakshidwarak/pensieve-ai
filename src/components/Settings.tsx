import React, { useState, useEffect } from 'react';
import { apiKeyApi, ApiKeyResponse } from '../services/apiKeyApi';
import './Settings.css';

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

const Settings: React.FC<SettingsProps> = ({ isOpen, onClose }) => {
  const [apiKey, setApiKey] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [hasApiKey, setHasApiKey] = useState(false);

  useEffect(() => {
    if (isOpen) {
      checkApiKeyStatus();
    }
  }, [isOpen]);

  const checkApiKeyStatus = async () => {
    try {
      const response = await apiKeyApi.getApiKeyStatus();
      setHasApiKey(response.has_key);
      setMessage(response.message);
    } catch (error) {
      console.error('Error checking API key status:', error);
      setMessage('Error checking API key status');
    }
  };

  const handleSaveApiKey = async () => {
    if (!apiKey.trim()) {
      setMessage('Please enter an API key');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await apiKeyApi.setApiKey(apiKey);
      setMessage(response.message);
      setHasApiKey(response.has_key);
      
      if (response.success) {
        setApiKey(''); // Clear the input after successful save
      }
    } catch (error) {
      console.error('Error setting API key:', error);
      setMessage('Failed to save API key. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearApiKey = () => {
    setApiKey('');
    setMessage('');
  };

  if (!isOpen) return null;

  return (
    <div className="settings-overlay">
      <div className="settings-modal">
        <div className="settings-header">
          <h2>Settings</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>
        
        <div className="settings-content">
          <div className="api-key-section">
            <h3>OpenAI API Key</h3>
            <p className="api-key-description">
              Enter your OpenAI API key to enable chat functionality. Your key is stored locally and securely.
            </p>
            
            <div className="api-key-status">
              <span className={`status-indicator ${hasApiKey ? 'has-key' : 'no-key'}`}>
                {hasApiKey ? '✓ API Key Set' : '⚠ No API Key'}
              </span>
            </div>

            <div className="api-key-input-group">
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your OpenAI API key (sk-...)"
                className="api-key-input"
                disabled={isLoading}
              />
              <div className="api-key-buttons">
                <button
                  onClick={handleSaveApiKey}
                  disabled={isLoading || !apiKey.trim()}
                  className="save-button"
                >
                  {isLoading ? 'Saving...' : 'Save Key'}
                </button>
                <button
                  onClick={handleClearApiKey}
                  disabled={isLoading}
                  className="clear-button"
                >
                  Clear
                </button>
              </div>
            </div>

            {message && (
              <div className={`message ${message.includes('Error') || message.includes('Failed') ? 'error' : 'success'}`}>
                {message}
              </div>
            )}

            <div className="api-key-help">
              <p>
                <strong>How to get your API key:</strong>
              </p>
              <ol>
                <li>Go to <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">OpenAI Platform</a></li>
                <li>Sign in to your account</li>
                <li>Click "Create new secret key"</li>
                <li>Copy the key and paste it above</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;

