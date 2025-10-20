import React from 'react';
import { commands } from '../types/commands';

const CommandHelp: React.FC = () => {
  return (
    <div className="command-help">
      <div className="help-header">
        <h3>Available Commands</h3>
        <p>Type any command and press <kbd>Tab</kbd> to expand the template</p>
      </div>
      
      <div className="commands-grid">
        {commands.map(command => (
          <div key={command.id} className="command-item">
            <div className="command-header">
              <span className="command-icon">{command.icon}</span>
              <span className="command-shortcut">{command.shortcut}</span>
            </div>
            <div className="command-description">{command.description}</div>
            <div className="command-example">
              <code>Type: {command.shortcut} + Tab</code>
            </div>
          </div>
        ))}
      </div>
      
      <div className="help-footer">
        <p><kbd>Tab</kbd> - Expand template</p>
        <p><kbd>Enter</kbd> - Execute command</p>
        <p><kbd>Esc</kbd> - Clear suggestions</p>
        <p><kbd>↑</kbd>/<kbd>↓</kbd> - Navigate history</p>
      </div>
    </div>
  );
};

export default CommandHelp;
