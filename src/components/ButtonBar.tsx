import React from 'react';
import { ButtonTemplate, CustomButton } from '../types';
import './ButtonBar.css';

interface ButtonBarProps {
  buttons: (ButtonTemplate | CustomButton)[];
  onButtonClick: (button: ButtonTemplate | CustomButton) => void;
  onAddCustom: () => void;
  onDeleteTemplate?: (templateId: string) => void;
}

const ButtonBar: React.FC<ButtonBarProps> = ({ buttons, onButtonClick, onAddCustom, onDeleteTemplate }) => {
  return (
    <div className="button-bar">
      <div className="button-bar-header">
        <h3>Tools</h3>
        <button className="add-button" onClick={onAddCustom} title="Add Custom Button">
          <span className="add-icon">+</span>
        </button>
      </div>
      
      <div className="buttons-grid">
        {buttons.map((button) => (
          <div key={button.id} className="button-container">
            <button
              className={`tool-button ${button.isCustom ? 'custom-button' : ''}`}
              onClick={() => onButtonClick(button)}
              title={button.template.title}
            >
              <span className="button-icon">{(button as any).icon || '📝'}</span>
              <span className="button-name">{button.name}</span>
              {button.isCustom && <span className="custom-indicator">★</span>}
            </button>
            {button.isCustom && onDeleteTemplate && (
              <button
                className="delete-button"
                onClick={(e) => {
                  e.stopPropagation();
                  if (window.confirm(`Are you sure you want to delete "${button.name}"?`)) {
                    onDeleteTemplate(button.id);
                  }
                }}
                title="Delete template"
              >
                ×
              </button>
            )}
          </div>
        ))}
      </div>
      
      <div className="button-bar-footer">
        <div className="footer-info">
          <span className="info-text">{buttons.length} tools available</span>
        </div>
      </div>
    </div>
  );
};

export default ButtonBar;
