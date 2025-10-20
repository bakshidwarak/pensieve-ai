export interface Command {
  id: string;
  name: string;
  shortcut: string;
  description: string;
  template: string;
  icon?: string;
}

export interface CommandResult {
  command: Command;
  content: string;
  cursorPosition?: number;
}

export interface SnippetVariable {
  name: string;
  value: string;
  placeholder?: string;
}

export const commands: Command[] = [
  {
    id: 'meet',
    name: 'Meeting',
    shortcut: 'meet',
    description: 'Create a meeting template',
    icon: '📅',
    template: `[MEETING]
Title : $0
Time: ${new Date().toLocaleString()}
Attendees: $1,$YOURS_TRULY
Notes:
[NOTE]
$2
[ENDNOTE]
[ENDMEETING]`
  },
  {
    id: 'interview',
    name: 'Interview',
    shortcut: 'interview',
    description: 'Create an interview template',
    icon: '🎯',
    template: `[INTERVIEW]
Candidate: $0
Position: $1
Date: ${new Date().toLocaleDateString()}
Interviewers: $2
Technical Skills:
$3
Soft Skills:
$4
Cultural Fit:
$5
Recommendation: $6
[ENDINTERVIEW]`
  },
  {
    id: 'feedback',
    name: 'Feedback',
    shortcut: 'feedback',
    description: 'Create a feedback template',
    icon: '💬',
    template: `[FEEDBACK]
Recipient: $0
Type: $1
Context:
$2
Specific Examples:
$3
Impact:
$4
Suggestions for Improvement:
$5
[ENDFEEDBACK]`
  },
  {
    id: 'todo',
    name: 'Todo',
    shortcut: 'todo',
    description: 'Create a todo template',
    icon: '✅',
    template: `[TODO]
Task: $0
Priority: $1
Due: $2
Assignee: $3
Status: $4
[ENDTODO]`
  },
  {
    id: 'project',
    name: 'Project',
    shortcut: 'project',
    description: 'Create a project template',
    icon: '📊',
    template: `[PROJECT]
Name: $1
Status: $2
Start Date: $3
End Date: $4
Team Members: $5
Objectives:
$6
Risks & Issues:
$7
Budget: $8
[ENDPROJECT]`
  },
  {
    id: 'decision',
    name: 'Decision',
    shortcut: 'decision',
    description: 'Create a decision template',
    icon: '⚖️',
    template: `[DECISION]
Title: $1
Context:
$2
Options:
$3
Decision Criteria:
$4
Pros & Cons:
$5
Recommendation:
$6
Decision Maker: $7
Deadline: $8
[ENDDECISION]`
  },
  {
    id: 'people',
    name: 'People Management',
    shortcut: 'people',
    description: 'Create a people management template',
    icon: '👥',
    template: `[PEOPLE]
Employee: $1
Role: $2
Manager: $3
Performance Notes:
$4
Development Goals:
$5
Strengths:
$6
Areas for Improvement:
$7
Next Review: $8
[ENDPEOPLE]`
  },
  {
    id: 'stakeholder',
    name: 'Stakeholder',
    shortcut: 'stakeholder',
    description: 'Create a stakeholder template',
    icon: '🤝',
    template: `[STAKEHOLDER]
Name: $1
Role: $2
Influence: $3
Interest: $4
Communication Preferences:
$5
Concerns & Expectations:
$6
Engagement Strategy:
$7
[ENDSTAKEHOLDER]`
  },
  {
    id: 'doc',
    name: 'Document',
    shortcut: 'doc',
    description: 'Create a document template',
    icon: '📄',
    template: `[DOC]
Title: $1
Type: $2
Author: $3
Date: ${new Date().toLocaleDateString()}
Content:
$4
[ENDDOC]`
  },
  {
    id: 'note',
    name: 'Note',
    shortcut: 'note',
    description: 'Create a quick note template',
    icon: '📝',
    template: `[NOTE] 
$0
[ENDNOTE]`
  },
  {
    id: 'idea',
    name: 'Idea',
    shortcut: 'idea',
    description: 'Create an idea template',
    icon: '💡',
    template: `[IDEA]
$1
Context: $2
Next Steps: $3
[ENDIDEA]`
  },
  {
    id: 'test',
    name: 'Test',
    shortcut: 'test',
    description: 'Simple test template',
    icon: '🧪',
    template: `Test $1 and $2 then $3`
  },
  {
    id: 'by',
    name: 'By',
    shortcut: 'by',
    description: 'Create a by template',
    icon: '👤',
    template: `BY [$1] $2`
  },
  {
    id: 'feedback',
    name: 'Feedback',
    shortcut: 'feed',
    description: 'Create a feedback template',
    icon: '💬',
    template: `[FEEDBACK] FOR [$1] FROM [$2] $3`
  },
  {
    id: 'todo',
    name: 'Todo',
    shortcut: 'ai',
    description: 'Create a todo template',
    icon: '✅',
    template: `${new Date().toLocaleDateString()} [TODO] $1`
  },
  {
    id: 'with',
    name: 'With',
    shortcut: 'w',
    description: 'Create a with template',
    icon: '🤝',
    template: `WITH [$1]$2`
  },
  {
    id: 'ref',
    name: 'Reference',
    shortcut: 'ref',
    description: 'Create a reference template',
    icon: '📚',
    template: `${new Date().toLocaleDateString()} [REFERENCE] ${'[clipboard]'} DESCRIPTION $1`
  }
];

export function findCommandByShortcut(shortcut: string): Command | undefined {
  return commands.find(cmd => cmd.shortcut.toLowerCase() === shortcut.toLowerCase());
}

export function processTemplate(template: string, variables: Record<string, string> = {}): string {
  let processed = template;
  
  // Replace timestamp placeholders
  processed = processed.replace(/\$\{new Date\(\)\.toLocaleString\(\)\}/g, new Date().toLocaleString());
  processed = processed.replace(/\$\{new Date\(\)\.toLocaleDateString\(\)\}/g, new Date().toLocaleDateString());
  
  // Don't replace numbered placeholders ($1, $2, etc.) as they are used for tab stops
  // Only replace them if they have custom values in variables
  for (const [key, value] of Object.entries(variables)) {
    if (key.startsWith('$') && value) {
      processed = processed.replace(new RegExp(`\\${key}`, 'g'), value);
    }
  }
  
  return processed;
}

export function findCursorPosition(template: string): number {
  const firstPlaceholder = template.match(/\$0/);
  return firstPlaceholder ? firstPlaceholder.index! : template.length;
}
