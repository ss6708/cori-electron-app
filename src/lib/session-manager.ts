/**
 * Session manager for frontend components.
 * Provides mechanisms for saving and restoring conversation state.
 */
import { Message } from "../types/message";
import { AgentState, AgentStateController } from "./state-controller";

export interface SessionData {
  messages: Message[];
  agentState: AgentState;
  stateMetadata: Record<string, unknown>;
  additionalData?: Record<string, unknown>;
  timestamp: string;
}

export class SessionManager {
  private readonly STORAGE_KEY = "cori_session_data";
  
  /**
   * Save the current session state to localStorage.
   * 
   * @param messages List of conversation messages
   * @param stateController Agent state controller
   * @param additionalData Optional additional data to save
   * @returns True if successfully saved, false otherwise
   */
  saveSession(
    messages: Message[], 
    stateController: AgentStateController,
    additionalData?: Record<string, unknown>
  ): boolean {
    try {
      const sessionData: SessionData = {
        messages,
        agentState: stateController.getState(),
        stateMetadata: stateController.getMetadata(),
        additionalData,
        timestamp: new Date().toISOString()
      };
      
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(sessionData));
      console.log("Session saved to localStorage");
      return true;
    } catch (error) {
      console.error("Error saving session:", error);
      return false;
    }
  }
  
  /**
   * Load the session state from localStorage.
   * 
   * @returns SessionData if successful, null otherwise
   */
  loadSession(): SessionData | null {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY);
      if (!data) {
        console.log("No saved session found");
        return null;
      }
      
      const sessionData: SessionData = JSON.parse(data);
      console.log("Session loaded from localStorage");
      return sessionData;
    } catch (error) {
      console.error("Error loading session:", error);
      return null;
    }
  }
  
  /**
   * Clear the saved session data.
   */
  clearSession(): void {
    localStorage.removeItem(this.STORAGE_KEY);
    console.log("Session cleared from localStorage");
  }
  
  /**
   * Check if a saved session exists.
   * 
   * @returns True if a saved session exists, false otherwise
   */
  hasSession(): boolean {
    return localStorage.getItem(this.STORAGE_KEY) !== null;
  }
  
  /**
   * Get the timestamp of the saved session.
   * 
   * @returns Timestamp string if a saved session exists, null otherwise
   */
  getSessionTimestamp(): string | null {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY);
      if (!data) return null;
      
      const sessionData: SessionData = JSON.parse(data);
      return sessionData.timestamp;
    } catch {
      return null;
    }
  }
}

// Create a global session manager instance
export const sessionManager = new SessionManager();
