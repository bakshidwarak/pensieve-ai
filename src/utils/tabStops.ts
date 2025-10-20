export interface TabStop {
  index: number;
  start: number;
  end: number;
  placeholder?: string;
}

export function findTabStops(template: string): TabStop[] {
  const tabStops: TabStop[] = [];
  const regex = /\$(\d+)(?::([^$]+))?/g;
  let match;
  
  while ((match = regex.exec(template)) !== null) {
    const index = parseInt(match[1]);
    const placeholder = match[2];
    tabStops.push({
      index,
      start: match.index,
      end: match.index + match[0].length,
      placeholder
    });
  }
  
  // Sort by index: $0 first, then $1, $2, etc.
  return tabStops.sort((a, b) => {
    return a.index - b.index; // $0 (index 0) comes first
  });
}

export function replaceTabStops(template: string): { content: string; tabStops: TabStop[] } {
  const originalTabStops = findTabStops(template);
  let content = template;
  const newTabStops: TabStop[] = [];
  let offset = 0;
  
  // Replace tab stops with placeholders or empty strings, but keep track of positions
  originalTabStops.forEach((tabStop) => {
    const replacement = tabStop.placeholder || '';
    const start = tabStop.start + offset;
    const end = tabStop.end + offset;
    
    content = content.substring(0, start) + replacement + content.substring(end);
    
    // Always create a tab stop, even if replacement is empty
    newTabStops.push({
      index: tabStop.index,
      start: start,
      end: start + replacement.length
    });
    
    offset += replacement.length - (tabStop.end - tabStop.start);
  });
  
  return { content, tabStops: newTabStops };
}

// Create navigable template that uses content markers for dynamic positioning
export function createNavigableTemplate(template: string): { content: string; tabStops: TabStop[] } {
  const originalTabStops = findTabStops(template);
  let content = template;
  const newTabStops: TabStop[] = [];
  let offset = 0;
  
  console.log('=== CREATING NAVIGABLE TEMPLATE ===');
  console.log('Original template:', template);
  console.log('Original tab stops:', originalTabStops);
  
  // Replace tab stops with visible placeholders and track their positions
  originalTabStops.forEach((tabStop) => {
    const start = tabStop.start + offset;
    const end = tabStop.end + offset;
    
    // Replace with placeholder text that's visible but distinct
    const placeholder = tabStop.placeholder || `[Tab Stop ${tabStop.index}]`;
    content = content.substring(0, start) + placeholder + content.substring(end);
    
    // Create tab stop at the placeholder position
    newTabStops.push({
      index: tabStop.index,
      start: start,
      end: start + placeholder.length
    });
    
    offset += placeholder.length - (tabStop.end - tabStop.start);
  });
  
  console.log('Processed content:', content);
  console.log('New tab stops:', newTabStops);
  
  return { content, tabStops: newTabStops };
}

export function findNextTabStop(tabStops: TabStop[], currentPosition: number): TabStop | null {
  return tabStops.find(tabStop => tabStop.start > currentPosition) || null;
}

export function findCurrentTabStop(tabStops: TabStop[], cursorPosition: number): TabStop | null {
  return tabStops.find(tabStop => 
    cursorPosition >= tabStop.start && cursorPosition <= tabStop.end
  ) || null;
}

// Find tab stops by scanning content for placeholders
export function findTabStopsInContent(content: string): TabStop[] {
  const tabStops: TabStop[] = [];
  // Look for [Tab Stop X] patterns
  const markerRegex = /\[Tab Stop (\d+)\]/g;
  let match;
  
  while ((match = markerRegex.exec(content)) !== null) {
    const index = parseInt(match[1]);
    tabStops.push({
      index,
      start: match.index,
      end: match.index + match[0].length
    });
  }
  
  // Sort by index: $0 first, then $1, $2, etc.
  return tabStops.sort((a, b) => a.index - b.index);
}

// Get the next tab stop after current position
export function getNextTabStop(content: string, currentPosition: number): TabStop | null {
  const tabStops = findTabStopsInContent(content);
  return tabStops.find(tabStop => tabStop.start > currentPosition) || null;
}

// Get the current tab stop at cursor position
export function getCurrentTabStop(content: string, cursorPosition: number): TabStop | null {
  const tabStops = findTabStopsInContent(content);
  return tabStops.find(tabStop => 
    cursorPosition >= tabStop.start && cursorPosition <= tabStop.end
  ) || null;
}
