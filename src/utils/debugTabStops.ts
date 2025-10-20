import { findTabStops, replaceTabStops } from './tabStops';

// Debug function to test tab stops
export function debugTabStops() {
  const testTemplate = '[MEETING]\nTitle : $1\nTime: [date]\nAttendees: $2\nNotes:\n[NOTE]\n$3\n[ENDNOTE]\n[ENDMEETING]$4';
  
  console.log('Original template:', testTemplate);
  
  const tabStops = findTabStops(testTemplate);
  console.log('Found tab stops:', tabStops);
  
  const { content, tabStops: processedTabStops } = replaceTabStops(testTemplate);
  console.log('Processed content:', content);
  console.log('Processed tab stops:', processedTabStops);
  
  return { content, tabStops: processedTabStops };
}
