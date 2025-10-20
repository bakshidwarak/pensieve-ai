import React, { useState } from 'react';
import { CustomButton, TemplateField } from '../types';
import './AddCustomButton.css';

interface AddCustomButtonProps {
  onSave: (button: CustomButton) => void;
  onCancel: () => void;
}

const AddCustomButton: React.FC<AddCustomButtonProps> = ({ onSave, onCancel }) => {
  const [buttonName, setButtonName] = useState('');
  const [buttonIcon, setButtonIcon] = useState('📝');
  const [templateTitle, setTemplateTitle] = useState('');
  const [fields, setFields] = useState<TemplateField[]>([]);
  const [newField, setNewField] = useState({
    label: '',
    type: 'text' as const,
    placeholder: '',
    required: false
  });

  const fieldTypes = [
    { value: 'text', label: 'Text Input' },
    { value: 'textarea', label: 'Text Area' },
    { value: 'date', label: 'Date' },
    { value: 'select', label: 'Dropdown' },
    { value: 'multiselect', label: 'Multiple Choice' }
  ];

  const commonIcons = ['📝', '📋', '📄', '📊', '📈', '📉', '🎯', '✅', '❌', '💡', '🔥', '⚡', '🎨', '🚀', '💎', '⭐', '🌟', '🎪', '🎭', '🎨'];

  const handleAddField = () => {
    if (newField.label.trim()) {
      const field: TemplateField = {
        id: `field_${Date.now()}`,
        label: newField.label,
        type: newField.type,
        placeholder: newField.placeholder,
        required: newField.required
      };
      setFields(prev => [...prev, field]);
      setNewField({
        label: '',
        type: 'text',
        placeholder: '',
        required: false
      });
    }
  };

  const handleRemoveField = (fieldId: string) => {
    setFields(prev => prev.filter(field => field.id !== fieldId));
  };

  const handleSave = () => {
    if (buttonName.trim() && templateTitle.trim()) {
      const customButton: CustomButton = {
        id: `custom_${Date.now()}`,
        name: buttonName,
        icon: buttonIcon,
        template: {
          title: templateTitle,
          fields: fields
        },
        isCustom: true
      };
      onSave(customButton);
    }
  };

  const canSave = buttonName.trim() && templateTitle.trim();

  return (
    <div className="add-custom-button">
      <div className="add-header">
        <h2>Create Custom Tool</h2>
        <button className="close-button" onClick={onCancel}>
          <span className="close-icon">×</span>
        </button>
      </div>

      <div className="add-content">
        <div className="form-section">
          <h3>Basic Information</h3>
          
          <div className="field-group">
            <label className="field-label">Tool Name *</label>
            <input
              type="text"
              value={buttonName}
              onChange={(e) => setButtonName(e.target.value)}
              placeholder="e.g., Daily Standup"
              className="form-input"
            />
          </div>

          <div className="field-group">
            <label className="field-label">Icon</label>
            <div className="icon-selector">
              <input
                type="text"
                value={buttonIcon}
                onChange={(e) => setButtonIcon(e.target.value)}
                className="form-input icon-input"
                maxLength={2}
              />
              <div className="icon-suggestions">
                {commonIcons.map(icon => (
                  <button
                    key={icon}
                    type="button"
                    className={`icon-option ${icon === buttonIcon ? 'selected' : ''}`}
                    onClick={() => setButtonIcon(icon)}
                  >
                    {icon}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="field-group">
            <label className="field-label">Template Title *</label>
            <input
              type="text"
              value={templateTitle}
              onChange={(e) => setTemplateTitle(e.target.value)}
              placeholder="e.g., Daily Standup Notes"
              className="form-input"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Template Fields</h3>
          
          <div className="field-builder">
            <div className="new-field-form">
              <div className="field-inputs">
                <input
                  type="text"
                  value={newField.label}
                  onChange={(e) => setNewField(prev => ({ ...prev, label: e.target.value }))}
                  placeholder="Field label"
                  className="form-input"
                />
                <select
                  value={newField.type}
                  onChange={(e) => setNewField(prev => ({ ...prev, type: e.target.value as any }))}
                  className="form-input"
                >
                  {fieldTypes.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
                <input
                  type="text"
                  value={newField.placeholder}
                  onChange={(e) => setNewField(prev => ({ ...prev, placeholder: e.target.value }))}
                  placeholder="Placeholder text"
                  className="form-input"
                />
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={newField.required}
                    onChange={(e) => setNewField(prev => ({ ...prev, required: e.target.checked }))}
                  />
                  Required
                </label>
              </div>
              <button
                type="button"
                onClick={handleAddField}
                className="add-field-btn"
                disabled={!newField.label.trim()}
              >
                Add Field
              </button>
            </div>

            <div className="fields-list">
              {fields.map(field => (
                <div key={field.id} className="field-item">
                  <div className="field-info">
                    <span className="field-label-text">{field.label}</span>
                    <span className="field-type">{field.type}</span>
                    {field.required && <span className="required-badge">Required</span>}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemoveField(field.id)}
                    className="remove-field-btn"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="add-footer">
        <button className="action-button secondary" onClick={onCancel}>
          Cancel
        </button>
        <button 
          className="action-button primary" 
          onClick={handleSave}
          disabled={!canSave}
        >
          Create Tool
        </button>
      </div>
    </div>
  );
};

export default AddCustomButton;
