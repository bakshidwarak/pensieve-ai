import React, { useState, useEffect } from 'react';
import { Template } from '../services/templateApi';
import './TemplateEditor.css';

interface TemplateEditorProps {
  template: Template | null;
  onSave: (template: Omit<Template, 'id' | 'is_builtin' | 'created_at' | 'updated_at'>) => void;
  onCancel: () => void;
  onDelete?: (templateId: string) => void;
  isBuiltIn?: boolean;
}

const TemplateEditor: React.FC<TemplateEditorProps> = ({ template, onSave, onCancel, onDelete, isBuiltIn = false }) => {
  const [formData, setFormData] = useState({
    name: '',
    shortcut: '',
    description: '',
    icon: '📝',
    template: ''
  });
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (template) {
      setFormData({
        name: template.name,
        shortcut: template.shortcut,
        description: template.description,
        icon: template.icon || '📝',
        template: template.template
      });
      setIsEditing(true);
    } else {
      setFormData({
        name: '',
        shortcut: '',
        description: '',
        icon: '📝',
        template: ''
      });
      setIsEditing(false);
    }
  }, [template]);

  const handleSave = () => {
    if (!formData.name.trim() || !formData.shortcut.trim() || !formData.template.trim()) {
      alert('Please fill in all required fields');
      return;
    }

    const newTemplate = {
      name: formData.name,
      shortcut: formData.shortcut,
      description: formData.description,
      icon: formData.icon,
      template: formData.template
    };

    onSave(newTemplate);
  };

  const handleDelete = () => {
    if (template && onDelete && window.confirm('Are you sure you want to delete this template?')) {
      onDelete(template.id);
    }
  };

  const insertTabStop = (stopNumber: number) => {
    const textarea = document.getElementById('template-content') as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = formData.template;
      const newText = text.substring(0, start) + `$${stopNumber}` + text.substring(end);
      setFormData(prev => ({ ...prev, template: newText }));
      
      // Focus back to textarea
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + 2, start + 2);
      }, 0);
    }
  };

  const insertFinalTabStop = () => {
    const textarea = document.getElementById('template-content') as HTMLTextAreaElement;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const text = formData.template;
      const newText = text.substring(0, start) + '$0' + text.substring(end);
      setFormData(prev => ({ ...prev, template: newText }));
      
      // Focus back to textarea
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + 2, start + 2);
      }, 0);
    }
  };

  const commonIcons = ['📝', '📋', '📄', '📊', '📈', '📉', '🎯', '✅', '❌', '💡', '🔥', '⚡', '🎨', '🚀', '💎', '⭐', '🌟', '🎪', '🎭', '👤', '🤝', '💬', '📅', '📚'];

  return (
    <div className="template-editor-modal">
      <div className="template-editor-content">
        <div className="template-editor-header">
          <h2>{isEditing ? 'Edit Template' : 'Create New Template'}</h2>
          <button className="close-button" onClick={onCancel}>×</button>
        </div>


        <div className="template-editor-form">
          <div className="form-row">
            <div className="form-group">
              <label>Template Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="e.g., Meeting Notes"
              />
            </div>
            <div className="form-group">
              <label>Shortcut *</label>
              <input
                type="text"
                value={formData.shortcut}
                onChange={(e) => setFormData(prev => ({ ...prev, shortcut: e.target.value }))}
                placeholder="e.g., meet"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Description</label>
              <input
                type="text"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Brief description of the template"
              />
            </div>
            <div className="form-group">
              <label>Icon</label>
              <div className="icon-selector">
                <input
                  type="text"
                  value={formData.icon}
                  onChange={(e) => setFormData(prev => ({ ...prev, icon: e.target.value }))}
                  maxLength={2}
                />
                <div className="icon-suggestions">
                  {commonIcons.map(icon => (
                    <button
                      key={icon}
                      type="button"
                      className={`icon-option ${icon === formData.icon ? 'selected' : ''}`}
                      onClick={() => setFormData(prev => ({ ...prev, icon }))}
                    >
                      {icon}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label>Template Content *</label>
            <div className="template-editor-container">
              <div className="tab-stop-buttons">
                <span>Insert Tab Stops:</span>
                {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(num => (
                  <button
                    key={num}
                    type="button"
                    className="tab-stop-btn"
                    onClick={() => insertTabStop(num)}
                  >
                    ${num}
                  </button>
                ))}
                <button
                  type="button"
                  className="tab-stop-btn final"
                  onClick={insertFinalTabStop}
                >
                  $0
                </button>
              </div>
              <textarea
                id="template-content"
                value={formData.template}
                onChange={(e) => setFormData(prev => ({ ...prev, template: e.target.value }))}
                placeholder="Enter your template content here. Use $1, $2, etc. for tab stops and $0 for final cursor position."
                rows={10}
              />
            </div>
          </div>

          <div className="template-preview">
            <h4>Preview:</h4>
            <pre>{formData.template}</pre>
          </div>
        </div>

        <div className="template-editor-footer">
          {isEditing && onDelete && (
            <button className="delete-button" onClick={handleDelete}>
              Delete Template
            </button>
          )}
          <div className="footer-buttons">
            <button className="cancel-button" onClick={onCancel}>
              Cancel
            </button>
            <button className="save-button" onClick={handleSave}>
              {isEditing ? 'Update' : 'Create'} Template
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateEditor;