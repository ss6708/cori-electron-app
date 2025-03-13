import { Message } from "../types/message";

/**
 * Send a message to the OpenAI API via the backend server
 * @param messages Array of messages representing the conversation history
 * @returns Promise with the AI response
 */
export async function sendMessageToAI(messages: Message[]): Promise<Message> {
  try {
    // Add retry logic to wait for backend to start
    let retries = 3;
    let response;
    
    while (retries > 0) {
      try {
        response = await fetch('http://localhost:5000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ messages }),
        });
        break; // If successful, exit the retry loop
      } catch (error) {
        retries--;
        if (retries === 0) throw error;
        console.log(`Backend connection failed, retrying... (${retries} attempts left)`);
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second before retrying
      }
    }

    if (!response!.ok) {
      throw new Error(`Server responded with status: ${response!.status}`);
    }

    return await response!.json();
  } catch (error) {
    console.error('Error sending message to AI:', error);
    return {
      role: 'system',
      content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : String(error)}`,
      timestamp: new Date().toISOString(),
      displayed: false,
    };
  }
}
