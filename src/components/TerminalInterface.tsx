import React, { useState, useRef, useEffect } from 'react';
import { commands, Command, processTemplate } from '../types/commands';
import CommandHelp from './CommandHelp';
import './TerminalInterface.css';

interface TerminalInterfaceProps {
  onCommandExecuted?: (command: Command, content: string) => void;
}

interface TerminalLine {
  id: string;
  type: 'input' | 'output' | 'command';
  content: string;
  timestamp: Date;
}

const TerminalInterface: React.FC<TerminalInterfaceProps> = ({ onCommandExecuted }) => {
  const [currentInput, setCurrentInput] = useState('');
  const [history, setHistory] = useState<TerminalLine[]>([
    {
      id: '1',
      type: 'output',
      content: 'Welcome to Pensieve - IDE for Leaders',
      timestamp: new Date()
    },
    {
      id: '2',
      type: 'output',
      content: 'Type a command and press Tab to expand. Type "help" for more information.',
      timestamp: new Date()
    }
  ]);
  const [currentLine, setCurrentLine] = useState<TerminalLine | null>(null);
  const [suggestions, setSuggestions] = useState<Command[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [history, currentLine]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setCurrentInput(value);

    // Find matching commands
    const matches = commands.filter(cmd => 
      cmd.shortcut.toLowerCase().startsWith(value.toLowerCase())
    );
    
    setSuggestions(matches);
    setShowSuggestions(value.length > 0 && matches.length > 0);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Tab' && currentInput.trim()) {
      e.preventDefault();
      
      const command = commands.find(cmd => 
        cmd.shortcut.toLowerCase() === currentInput.toLowerCase()
      );
      
      if (command) {
        executeCommand(command);
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      executeCurrentInput();
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setSuggestions([]);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      // TODO: Implement history navigation
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      // TODO: Implement history navigation
    }
  };

  const executeCommand = (command: Command) => {
    const template = processTemplate(command.template);
    
    // Add input line to history
    const inputLine: TerminalLine = {
      id: Date.now().toString(),
      type: 'input',
      content: `$ ${currentInput}`,
      timestamp: new Date()
    };
    
    setHistory(prev => [...prev, inputLine]);
    
    // Create current line with template
    const templateLine: TerminalLine = {
      id: (Date.now() + 1).toString(),
      type: 'command',
      content: template,
      timestamp: new Date()
    };
    
    setCurrentLine(templateLine);
    setCurrentInput('');
    setShowSuggestions(false);
    setSuggestions([]);
    
    if (onCommandExecuted) {
      onCommandExecuted(command, template);
    }
  };

  const executeCurrentInput = () => {
    if (currentInput.trim()) {
      const input = currentInput.toLowerCase().trim();
      
      if (input === 'help') {
        setShowHelp(true);
        setCurrentInput('');
        return;
      }
      
      if (input === 'clear') {
        clearTerminal();
        return;
      }
      
      const command = commands.find(cmd => 
        cmd.shortcut.toLowerCase() === input
      );
      
      if (command) {
        executeCommand(command);
      } else {
        // Add as regular input
        const inputLine: TerminalLine = {
          id: Date.now().toString(),
          type: 'input',
          content: `$ ${currentInput}`,
          timestamp: new Date()
        };
        
        setHistory(prev => [...prev, inputLine]);
        
        // Add error message
        const errorLine: TerminalLine = {
          id: (Date.now() + 1).toString(),
          type: 'output',
          content: `Command not found: ${currentInput}. Type "help" for available commands.`,
          timestamp: new Date()
        };
        
        setHistory(prev => [...prev, errorLine]);
        setCurrentInput('');
      }
    }
  };

  const handleSuggestionClick = (command: Command) => {
    setCurrentInput(command.shortcut);
    setShowSuggestions(false);
    executeCommand(command);
  };

  const clearTerminal = () => {
    setHistory([]);
    setCurrentLine(null);
    setCurrentInput('');
    setShowSuggestions(false);
    setShowHelp(false);
  };

  return (
    <div className="terminal-interface">
      <div className="terminal-header">
        <div className="terminal-controls">
          <div className="control-dot red"></div>
          <div className="control-dot yellow"></div>
          <div className="control-dot green"></div>
        </div>
        <div className="terminal-title">
          <span className="terminal-icon">⚡</span>
          Pensieve Terminal
        </div>
        <div className="terminal-actions">
          <button className="clear-btn" onClick={clearTerminal}>Clear</button>
        </div>
      </div>
      
      <div className="terminal-content" ref={terminalRef}>
        {showHelp && <CommandHelp />}
        
        {history.map(line => (
          <div key={line.id} className={`terminal-line ${line.type}`}>
            {line.type === 'input' && (
              <span className="prompt">$</span>
            )}
            <span className="content">{line.content}</span>
            {line.type === 'output' && (
              <span className="timestamp">{line.timestamp.toLocaleTimeString()}</span>
            )}
          </div>
        ))}
        
        {currentLine && (
          <div className="terminal-line command">
            <div className="template-content">
              <pre>{currentLine.content}</pre>
            </div>
          </div>
        )}
        
        <div className="terminal-input-line">
          <span className="prompt">$</span>
          <div className="input-container">
            <input
              ref={inputRef}
              type="text"
              value={currentInput}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Type a command..."
              className="terminal-input"
              autoFocus
            />
            {showSuggestions && suggestions.length > 0 && (
              <div className="suggestions">
                {suggestions.map(command => (
                  <div
                    key={command.id}
                    className="suggestion-item"
                    onClick={() => handleSuggestionClick(command)}
                  >
                    <span className="suggestion-icon">{command.icon}</span>
                    <span className="suggestion-shortcut">{command.shortcut}</span>
                    <span className="suggestion-desc">{command.description}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TerminalInterface;
