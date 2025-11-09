import { useState, useEffect } from 'react';
import { templatesApi, Template, TemplateCreate } from '../services/templatesApi';
import './TemplateManager.css';

function TemplateManager() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [formData, setFormData] = useState<TemplateCreate>({
    trigger: '',
    label: '',
    description: '',
    content: '',
    category: '',
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await templatesApi.getAll();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleCreate = async () => {
    try {
      await templatesApi.create(formData);
      setFormData({
        trigger: '',
        label: '',
        description: '',
        content: '',
        category: '',
      });
      setShowCreateForm(false);
      loadTemplates();
    } catch (error) {
      console.error('Failed to create template:', error);
      alert('Failed to create template');
    }
  };

  const handleEdit = (template: Template) => {
    setEditingTemplate(template);
    setFormData({
      trigger: template.trigger,
      label: template.label,
      description: template.description || '',
      content: template.content,
      category: template.category || '',
    });
    setShowCreateForm(false);
  };

  const handleUpdate = async () => {
    if (!editingTemplate) return;

    try {
      await templatesApi.update(editingTemplate.id, formData);
      setFormData({
        trigger: '',
        label: '',
        description: '',
        content: '',
        category: '',
      });
      setEditingTemplate(null);
      loadTemplates();
    } catch (error) {
      console.error('Failed to update template:', error);
      alert('Failed to update template');
    }
  };

  const handleCancelEdit = () => {
    setEditingTemplate(null);
    setFormData({
      trigger: '',
      label: '',
      description: '',
      content: '',
      category: '',
    });
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this template?')) return;

    try {
      await templatesApi.delete(id);
      loadTemplates();
    } catch (error) {
      console.error('Failed to delete template:', error);
      alert('Failed to delete template');
    }
  };

  const systemTemplates = templates.filter(t => t.is_system);
  const userTemplates = templates.filter(t => !t.is_system);

  return (
    <div className="template-manager">
      <div className="template-header">
        <h2>Templates</h2>
        <button
          className="create-btn"
          onClick={() => setShowCreateForm(!showCreateForm)}
        >
          + New Template
        </button>
      </div>

      {(showCreateForm || editingTemplate) && (
        <div className="template-form">
          <h3>{editingTemplate ? 'Edit Template' : 'Create New Template'}</h3>
          <div className="form-group">
            <label>Trigger (e.g., "meet", "todo")</label>
            <input
              type="text"
              value={formData.trigger}
              onChange={(e) => setFormData({ ...formData, trigger: e.target.value })}
              placeholder="meet"
            />
          </div>
          <div className="form-group">
            <label>Label</label>
            <input
              type="text"
              value={formData.label}
              onChange={(e) => setFormData({ ...formData, label: e.target.value })}
              placeholder="Meeting Notes"
            />
          </div>
          <div className="form-group">
            <label>Category (optional)</label>
            <input
              type="text"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              placeholder="meeting"
            />
          </div>
          <div className="form-group">
            <label>Description (optional)</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Template for meeting notes"
            />
          </div>
          <div className="form-group">
            <label>Content (use {`{{variable}}`} for placeholders, $0 $1 $2 for tab stops)</label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              placeholder="# {{title}}\nDate: {{date}}\n\n$0"
              rows={10}
            />
          </div>
          <div className="form-actions">
            {editingTemplate ? (
              <>
                <button className="save-btn" onClick={handleUpdate}>
                  Save Changes
                </button>
                <button className="cancel-btn" onClick={handleCancelEdit}>
                  Cancel
                </button>
              </>
            ) : (
              <>
                <button className="save-btn" onClick={handleCreate}>
                  Create
                </button>
                <button className="cancel-btn" onClick={() => setShowCreateForm(false)}>
                  Cancel
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* System Templates */}
      <div className="templates-section">
        <h3>System Templates</h3>
        <div className="templates-grid">
          {systemTemplates.map((template) => (
            <div
              key={template.id}
              className="template-card"
            >
              <div
                className="template-content"
                onClick={() => setSelectedTemplate(template)}
              >
                <div className="template-trigger">{template.trigger}</div>
                <div className="template-label">{template.label}</div>
                {template.description && (
                  <div className="template-description">{template.description}</div>
                )}
              </div>
              <button
                className="edit-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  handleEdit(template);
                }}
              >
                Edit
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* User Templates */}
      {userTemplates.length > 0 && (
        <div className="templates-section">
          <h3>My Templates</h3>
          <div className="templates-grid">
            {userTemplates.map((template) => (
              <div
                key={template.id}
                className="template-card user-template"
              >
                <div
                  className="template-content"
                  onClick={() => setSelectedTemplate(template)}
                >
                  <div className="template-trigger">{template.trigger}</div>
                  <div className="template-label">{template.label}</div>
                  {template.description && (
                    <div className="template-description">{template.description}</div>
                  )}
                </div>
                <div className="template-actions">
                  <button
                    className="edit-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEdit(template);
                    }}
                  >
                    Edit
                  </button>
                  <button
                    className="delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(template.id);
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Template Preview */}
      {selectedTemplate && (
        <div className="template-preview-modal" onClick={() => setSelectedTemplate(null)}>
          <div className="template-preview" onClick={(e) => e.stopPropagation()}>
            <div className="preview-header">
              <h3>{selectedTemplate.label}</h3>
              <button onClick={() => setSelectedTemplate(null)}>×</button>
            </div>
            <div className="preview-meta">
              <span className="preview-trigger">Trigger: {selectedTemplate.trigger}</span>
              {selectedTemplate.category && (
                <span className="preview-category">Category: {selectedTemplate.category}</span>
              )}
            </div>
            {selectedTemplate.description && (
              <p className="preview-description">{selectedTemplate.description}</p>
            )}
            <div className="preview-content">
              <h4>Template Content:</h4>
              <pre>{selectedTemplate.content}</pre>
            </div>
            {selectedTemplate.variables && selectedTemplate.variables.length > 0 && (
              <div className="preview-variables">
                <h4>Variables:</h4>
                <div className="variables-list">
                  {selectedTemplate.variables.map((variable) => (
                    <span key={variable} className="variable-badge">
                      {`{{${variable}}}`}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default TemplateManager;
