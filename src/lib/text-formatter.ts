"use client"

import * as React from "react"

/**
 * Text formatter utility for improving the display of AI responses
 */

/**
 * Format text from OpenAI responses to improve readability
 * - Converts markdown-style bold (**text**) to HTML bold tags
 * - Creates proper line breaks for numbered lists and bullet points
 * - Breaks up large text blocks into smaller paragraphs
 * 
 * @param text The raw text from OpenAI response
 * @returns Formatted text with proper HTML formatting
 */
export function formatAIResponse(text: string): string {
  if (!text) return '';
  
  // Step 1: Convert markdown-style bold to HTML bold tags
  let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Step 2: Ensure proper line breaks before numbered lists and bullet points
  formattedText = formattedText.replace(/(\d+\.\s*\*\*.*?\*\*)/g, '\n$1');
  formattedText = formattedText.replace(/(\d+\.\s*<strong>.*?<\/strong>)/g, '\n$1');
  formattedText = formattedText.replace(/(\d+\.\s)/g, '\n$1');
  formattedText = formattedText.replace(/(-\s)/g, '\n- ');
  formattedText = formattedText.replace(/(\•\s)/g, '\n• ');
  
  // Step 3: Break up large paragraphs (more than 150 chars without breaks)
  const paragraphs = formattedText.split('\n');
  const formattedParagraphs = paragraphs.map(paragraph => {
    if (paragraph.length > 150 && !paragraph.includes('<strong>') && 
        !paragraph.startsWith('- ') && !paragraph.startsWith('• ') && 
        !/^\d+\./.test(paragraph)) {
      // Try to break at sentence endings
      return paragraph.replace(/([.!?])\s+/g, '$1\n');
    }
    return paragraph;
  });
  
  // Step 4: Join everything back together with proper line breaks
  formattedText = formattedParagraphs.join('\n');
  
  // Step 5: Ensure consistent spacing (no multiple consecutive line breaks)
  formattedText = formattedText.replace(/\n{3,}/g, '\n\n');
  
  return formattedText;
}

/**
 * Convert formatted text with line breaks to React-friendly JSX
 * This function splits text by line breaks and wraps each line in appropriate elements
 * 
 * @param text Formatted text with line breaks
 * @returns Array of JSX elements
 */
export function textToJSX(text: string): React.ReactNode[] {
  if (!text) return [];
  
  // Split by line breaks
  const lines = text.split('\n');
  
  // Convert each line to a JSX element
  return lines.map((line, index) => {
    // Skip empty lines
    if (!line.trim()) return null;
    
    // For lines that are bullet points or numbered lists
    if (line.trim().startsWith('- ') || line.trim().startsWith('• ') || /^\d+\./.test(line.trim())) {
      return React.createElement('div', {
        key: index,
        className: "ml-4 my-1",
        dangerouslySetInnerHTML: { __html: line }
      });
    }
    
    // For regular paragraphs
    return React.createElement('p', {
      key: index,
      className: "my-1",
      dangerouslySetInnerHTML: { __html: line }
    });
  }).filter(Boolean); // Remove null elements
}
