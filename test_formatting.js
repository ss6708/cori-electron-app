// Test script for text formatting
const formatAIResponse = (text) => {
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
};

// Test cases
const testCases = [
  {
    name: "Numbered list with bold titles",
    input: "5.**[Exit Strategy]** Estimate the exit value. - **Exit Multiple**: Choose an appropriate exit multiple for EBITDA.",
    expected: "Contains proper line breaks and bold formatting"
  },
  {
    name: "Bullet points",
    input: "- First bullet point\n- Second bullet point with **bold text**",
    expected: "Preserves bullet points and formats bold text"
  },
  {
    name: "Large paragraph",
    input: "This is a very long paragraph that should be broken up into smaller paragraphs. It contains more than 150 characters and should be split at sentence endings. This is the second sentence. And this is the third sentence which should create another paragraph break.",
    expected: "Breaks large paragraphs at sentence endings"
  },
  {
    name: "Example from screenshot",
    input: "5.**[Exit Strategy]** Estimate the exit value. - **Exit Multiple**: Choose an appropriate exit multiple for EBITDA. - **Projected Returns**: Calculate IRR and equity multiple based on the exit value.",
    expected: "Formats numbered list with bold titles and creates proper line breaks"
  }
];

// Run tests
console.log("Testing text formatting functions:");
console.log("=================================");

testCases.forEach(test => {
  console.log(`\nTest: ${test.name}`);
  console.log(`Input: ${test.input.substring(0, 50)}${test.input.length > 50 ? '...' : ''}`);
  const formatted = formatAIResponse(test.input);
  console.log(`\nFormatted output:\n${formatted}`);
  console.log(`\nExpected: ${test.expected}`);
});
