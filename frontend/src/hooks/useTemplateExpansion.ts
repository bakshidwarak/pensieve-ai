import { useState, useEffect, useCallback } from 'react';
import { templatesApi, Template } from '../services/templatesApi';

export const useTemplateExpansion = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await templatesApi.getAll();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Extract template trigger from current text position
   * Returns the trigger word if found (e.g., "meet", "todo")
   */
  const extractTrigger = useCallback((text: string, cursorPosition: number): string | null => {
    // Get text up to cursor
    const textBeforeCursor = text.substring(0, cursorPosition);

    // Find the last word before cursor (allowing word boundaries)
    const match = textBeforeCursor.match(/(\w+)$/);

    if (!match) return null;

    return match[1].toLowerCase();
  }, []);

  /**
   * Check if a trigger word matches a template
   */
  const findTemplate = useCallback((trigger: string): Template | null => {
    return templates.find(t => t.trigger.toLowerCase() === trigger.toLowerCase()) || null;
  }, [templates]);

  /**
   * Expand template content with default values and tab stops
   * Supports both {{variable}} and $0, $1, $2 syntax
   * Returns both the expanded content and tab stop positions
   */
  const expandTemplate = useCallback((template: Template): { content: string; tabStops: number[] } => {
    let content = template.content;
    const tabStopMap = new Map<number, number>(); // tab stop number -> position

    // First pass: Replace {{variable}} placeholders with defaults
    // We need to track how the content length changes to adjust tab stops
    let lengthDiff = 0;
    const placeholderRegex = /\{\{(\w+)\}\}/g;
    const replacements: Array<{ start: number; end: number; replacement: string }> = [];

    let match;
    while ((match = placeholderRegex.exec(template.content)) !== null) {
      const variable = match[1];
      const now = new Date();
      const dateStr = now.toISOString().split('T')[0];
      const timeStr = now.toLocaleTimeString();

      let replacement = '';
      switch (variable.toLowerCase()) {
        case 'date':
          replacement = dateStr;
          break;
        case 'time':
          replacement = timeStr;
          break;
        case 'datetime':
          replacement = `${dateStr} ${timeStr}`;
          break;
        default:
          replacement = ''; // Leave blank for user to fill
      }

      replacements.push({
        start: match.index,
        end: match.index + match[0].length,
        replacement: replacement
      });
    }

    // Apply replacements in reverse order
    replacements.reverse().forEach(r => {
      content = content.substring(0, r.start) + r.replacement + content.substring(r.end);
    });

    // Second pass: Find all $n tab stops and record their positions
    const tabStopRegex = /\$(\d+)/g;
    const tabStopMatches: Array<{ index: number; stopNumber: number; length: number }> = [];

    while ((match = tabStopRegex.exec(content)) !== null) {
      tabStopMatches.push({
        index: match.index,
        stopNumber: parseInt(match[1]),
        length: match[0].length
      });
    }

    // Sort by position (reverse order for replacement)
    tabStopMatches.sort((a, b) => b.index - a.index);

    // Replace $n markers and track their positions
    for (const stop of tabStopMatches) {
      const before = content.substring(0, stop.index);
      const after = content.substring(stop.index + stop.length);
      content = before + after;

      // Store the position for this tab stop number
      tabStopMap.set(stop.stopNumber, stop.index);
    }

    // Convert tab stop map to sorted array of positions
    const sortedTabStops = Array.from(tabStopMap.entries())
      .sort(([a], [b]) => a - b) // Sort by tab stop number
      .map(([_, position]) => position);

    return { content, tabStops: sortedTabStops };
  }, []);

  /**
   * Handle tab key press to expand template
   * Returns expanded content if template found, null otherwise
   */
  const handleTabExpansion = useCallback((
    text: string,
    cursorPosition: number
  ): { content: string; newCursorPosition: number; tabStops: number[] } | null => {
    const trigger = extractTrigger(text, cursorPosition);

    if (!trigger) return null;

    const template = findTemplate(trigger);

    if (!template) return null;

    // Get text before and after the trigger
    const textBeforeTrigger = text.substring(0, cursorPosition - trigger.length);
    const textAfterCursor = text.substring(cursorPosition);

    // Expand template with tab stops
    const { content: expandedContent, tabStops: relativeTabStops } = expandTemplate(template);

    // Combine: text before + expanded template + text after
    const newContent = textBeforeTrigger + expandedContent + textAfterCursor;

    // Adjust tab stop positions to account for text before trigger
    const absoluteTabStops = relativeTabStops.map(pos => textBeforeTrigger.length + pos);

    // Calculate new cursor position (first tab stop, or end of template if no tab stops)
    const newCursorPosition = absoluteTabStops.length > 0
      ? absoluteTabStops[0]
      : textBeforeTrigger.length + expandedContent.length;

    return {
      content: newContent,
      newCursorPosition,
      tabStops: absoluteTabStops,
    };
  }, [extractTrigger, findTemplate, expandTemplate]);

  /**
   * Get template suggestions for autocomplete
   */
  const getSuggestions = useCallback((trigger: string): Template[] => {
    if (!trigger) return [];

    const lowerTrigger = trigger.toLowerCase();
    return templates.filter(t =>
      t.trigger.toLowerCase().startsWith(lowerTrigger)
    );
  }, [templates]);

  return {
    templates,
    loading,
    handleTabExpansion,
    getSuggestions,
    expandTemplate,
    findTemplate,
    reloadTemplates: loadTemplates,
  };
};
