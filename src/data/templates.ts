import { ButtonTemplate } from '../types';

export const defaultTemplates: ButtonTemplate[] = [
  {
    id: 'meeting',
    name: 'Meeting',
    icon: '📅',
    template: {
      title: 'Meeting Notes',
      fields: [
        { id: 'title', label: 'Meeting Title', type: 'text', required: true, placeholder: 'Enter meeting title' },
        { id: 'date', label: 'Date', type: 'date', required: true },
        { id: 'attendees', label: 'Attendees', type: 'text', placeholder: 'Who attended the meeting?' },
        { id: 'agenda', label: 'Agenda', type: 'textarea', placeholder: 'What was discussed?' },
        { id: 'action_items', label: 'Action Items', type: 'textarea', placeholder: 'What needs to be done next?' },
        { id: 'decisions', label: 'Decisions Made', type: 'textarea', placeholder: 'What decisions were made?' }
      ]
    }
  },
  {
    id: 'feedback',
    name: 'Feedback',
    icon: '💬',
    template: {
      title: 'Feedback Session',
      fields: [
        { id: 'recipient', label: 'Recipient', type: 'text', required: true, placeholder: 'Who is this feedback for?' },
        { id: 'type', label: 'Feedback Type', type: 'select', required: true, options: ['Positive', 'Constructive', 'Performance', 'Behavioral'] },
        { id: 'context', label: 'Context', type: 'textarea', placeholder: 'What situation prompted this feedback?' },
        { id: 'specific_examples', label: 'Specific Examples', type: 'textarea', placeholder: 'Provide specific examples' },
        { id: 'impact', label: 'Impact', type: 'textarea', placeholder: 'What was the impact?' },
        { id: 'suggestions', label: 'Suggestions for Improvement', type: 'textarea', placeholder: 'How can they improve?' }
      ]
    }
  },
  {
    id: 'todo',
    name: 'Todo',
    icon: '✅',
    template: {
      title: 'Task Management',
      fields: [
        { id: 'task', label: 'Task', type: 'text', required: true, placeholder: 'What needs to be done?' },
        { id: 'priority', label: 'Priority', type: 'select', required: true, options: ['High', 'Medium', 'Low'] },
        { id: 'due_date', label: 'Due Date', type: 'date' },
        { id: 'assignee', label: 'Assignee', type: 'text', placeholder: 'Who is responsible?' },
        { id: 'description', label: 'Description', type: 'textarea', placeholder: 'Additional details' },
        { id: 'status', label: 'Status', type: 'select', options: ['Not Started', 'In Progress', 'Completed', 'Blocked'] }
      ]
    }
  },
  {
    id: 'document',
    name: 'Document',
    icon: '📄',
    template: {
      title: 'Document',
      fields: [
        { id: 'title', label: 'Document Title', type: 'text', required: true, placeholder: 'Enter document title' },
        { id: 'type', label: 'Document Type', type: 'select', options: ['Report', 'Proposal', 'Policy', 'Procedure', 'Presentation', 'Other'] },
        { id: 'author', label: 'Author', type: 'text', placeholder: 'Who created this document?' },
        { id: 'content', label: 'Content', type: 'textarea', placeholder: 'Document content goes here...' },
        { id: 'tags', label: 'Tags', type: 'text', placeholder: 'Comma-separated tags' },
        { id: 'version', label: 'Version', type: 'text', placeholder: 'v1.0' }
      ]
    }
  },
  {
    id: 'interview',
    name: 'Interview',
    icon: '🎯',
    template: {
      title: 'Interview Notes',
      fields: [
        { id: 'candidate', label: 'Candidate Name', type: 'text', required: true, placeholder: 'Candidate full name' },
        { id: 'position', label: 'Position', type: 'text', required: true, placeholder: 'Role being interviewed for' },
        { id: 'date', label: 'Interview Date', type: 'date', required: true },
        { id: 'interviewers', label: 'Interviewers', type: 'text', placeholder: 'Who conducted the interview?' },
        { id: 'technical_skills', label: 'Technical Skills', type: 'textarea', placeholder: 'Assessment of technical abilities' },
        { id: 'soft_skills', label: 'Soft Skills', type: 'textarea', placeholder: 'Communication, teamwork, leadership' },
        { id: 'cultural_fit', label: 'Cultural Fit', type: 'textarea', placeholder: 'Alignment with company values' },
        { id: 'recommendation', label: 'Recommendation', type: 'select', options: ['Strong Hire', 'Hire', 'No Hire', 'Strong No Hire'] }
      ]
    }
  },
  {
    id: 'project',
    name: 'Project Management',
    icon: '📊',
    template: {
      title: 'Project Management',
      fields: [
        { id: 'project_name', label: 'Project Name', type: 'text', required: true, placeholder: 'Project title' },
        { id: 'status', label: 'Status', type: 'select', options: ['Planning', 'In Progress', 'On Hold', 'Completed', 'Cancelled'] },
        { id: 'start_date', label: 'Start Date', type: 'date' },
        { id: 'end_date', label: 'End Date', type: 'date' },
        { id: 'team_members', label: 'Team Members', type: 'text', placeholder: 'Who is on the team?' },
        { id: 'objectives', label: 'Objectives', type: 'textarea', placeholder: 'What are the main goals?' },
        { id: 'risks', label: 'Risks & Issues', type: 'textarea', placeholder: 'Potential problems and mitigation strategies' },
        { id: 'budget', label: 'Budget', type: 'text', placeholder: 'Project budget' }
      ]
    }
  },
  {
    id: 'stakeholder',
    name: 'Stakeholder Management',
    icon: '🤝',
    template: {
      title: 'Stakeholder Management',
      fields: [
        { id: 'stakeholder_name', label: 'Stakeholder Name', type: 'text', required: true, placeholder: 'Name or organization' },
        { id: 'role', label: 'Role', type: 'text', placeholder: 'Their role in the project/company' },
        { id: 'influence', label: 'Influence Level', type: 'select', options: ['High', 'Medium', 'Low'] },
        { id: 'interest', label: 'Interest Level', type: 'select', options: ['High', 'Medium', 'Low'] },
        { id: 'communication_preferences', label: 'Communication Preferences', type: 'textarea', placeholder: 'How they prefer to be contacted' },
        { id: 'concerns', label: 'Concerns & Expectations', type: 'textarea', placeholder: 'What are their main concerns?' },
        { id: 'engagement_strategy', label: 'Engagement Strategy', type: 'textarea', placeholder: 'How to keep them engaged' }
      ]
    }
  },
  {
    id: 'stories',
    name: 'Stories',
    icon: '📖',
    template: {
      title: 'User Stories',
      fields: [
        { id: 'title', label: 'Story Title', type: 'text', required: true, placeholder: 'Brief description of the story' },
        { id: 'as_a', label: 'As a...', type: 'text', placeholder: 'Who is the user?' },
        { id: 'i_want', label: 'I want...', type: 'text', placeholder: 'What do they want to do?' },
        { id: 'so_that', label: 'So that...', type: 'text', placeholder: 'Why do they want this?' },
        { id: 'acceptance_criteria', label: 'Acceptance Criteria', type: 'textarea', placeholder: 'How do we know when it\'s done?' },
        { id: 'priority', label: 'Priority', type: 'select', options: ['Critical', 'High', 'Medium', 'Low'] },
        { id: 'story_points', label: 'Story Points', type: 'text', placeholder: 'Estimation (1, 2, 3, 5, 8, 13)' }
      ]
    }
  },
  {
    id: 'people',
    name: 'People Management',
    icon: '👥',
    template: {
      title: 'People Management',
      fields: [
        { id: 'employee_name', label: 'Employee Name', type: 'text', required: true, placeholder: 'Full name' },
        { id: 'role', label: 'Role/Title', type: 'text', placeholder: 'Current position' },
        { id: 'manager', label: 'Manager', type: 'text', placeholder: 'Who do they report to?' },
        { id: 'performance_notes', label: 'Performance Notes', type: 'textarea', placeholder: 'Recent performance observations' },
        { id: 'development_goals', label: 'Development Goals', type: 'textarea', placeholder: 'Career development objectives' },
        { id: 'strengths', label: 'Strengths', type: 'textarea', placeholder: 'Key strengths and skills' },
        { id: 'areas_for_improvement', label: 'Areas for Improvement', type: 'textarea', placeholder: 'Growth opportunities' },
        { id: 'next_review_date', label: 'Next Review Date', type: 'date' }
      ]
    }
  },
  {
    id: 'decision',
    name: 'Decision Making',
    icon: '⚖️',
    template: {
      title: 'Decision Making',
      fields: [
        { id: 'decision_title', label: 'Decision Title', type: 'text', required: true, placeholder: 'What decision needs to be made?' },
        { id: 'context', label: 'Context', type: 'textarea', placeholder: 'Background and current situation' },
        { id: 'options', label: 'Options', type: 'textarea', placeholder: 'Available choices and alternatives' },
        { id: 'criteria', label: 'Decision Criteria', type: 'textarea', placeholder: 'Factors to consider' },
        { id: 'pros_cons', label: 'Pros & Cons', type: 'textarea', placeholder: 'Benefits and drawbacks of each option' },
        { id: 'recommendation', label: 'Recommendation', type: 'textarea', placeholder: 'Recommended decision and rationale' },
        { id: 'decision_maker', label: 'Decision Maker', type: 'text', placeholder: 'Who has the authority to decide?' },
        { id: 'deadline', label: 'Decision Deadline', type: 'date' }
      ]
    }
  }
];
