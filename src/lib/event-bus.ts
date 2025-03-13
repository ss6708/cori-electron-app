/**
 * Event bus for frontend components.
 * Provides a pub/sub mechanism for decoupling components.
 */

export interface Event<T = unknown> {
  type: string;
  data?: T;
  timestamp: string;
}

export class EventBus {
  private subscribers: Map<string, Array<(event: Event) => void>> = new Map();
  private history: Event[] = [];
  
  /**
   * Subscribe to events of a specific type.
   * 
   * @param eventType Type of events to subscribe to
   * @param callback Function to call when an event of this type is published
   * @returns Unsubscribe function
   */
  subscribe(eventType: string, callback: (event: Event) => void): () => void {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, []);
    }
    
    this.subscribers.get(eventType)!.push(callback);
    
    // Return unsubscribe function
    return () => {
      const callbacks = this.subscribers.get(eventType);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index !== -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }
  
  /**
   * Publish an event to all subscribers.
   * 
   * @param eventType Type of event to publish
   * @param data Optional data to include with the event
   */
  publish<T = unknown>(eventType: string, data?: T): void {
    const event: Event<T> = {
      type: eventType,
      data,
      timestamp: new Date().toISOString()
    };
    
    // Add to history
    this.history.push(event);
    
    // Notify subscribers
    if (this.subscribers.has(eventType)) {
      this.subscribers.get(eventType)!.forEach(callback => {
        try {
          callback(event);
        } catch (error) {
          console.error(`Error in event callback for ${eventType}:`, error);
        }
      });
    }
  }
  
  /**
   * Get event history with optional filtering.
   * 
   * @param eventType Optional filter by event type
   * @param limit Maximum number of events to return
   * @returns List of events matching the criteria
   */
  getHistory(eventType?: string, limit?: number): Event[] {
    let filtered = this.history;
    
    // Filter by event type
    if (eventType) {
      filtered = filtered.filter(event => event.type === eventType);
    }
    
    // Apply limit
    if (limit && limit > 0) {
      filtered = filtered.slice(-limit);
    }
    
    return filtered;
  }
  
  /**
   * Clear the event history.
   */
  clearHistory(): void {
    this.history = [];
  }
  
  /**
   * Save event history to localStorage.
   * 
   * @param key Key to save the history under
   */
  saveHistory(key: string = 'event_history'): void {
    try {
      localStorage.setItem(key, JSON.stringify(this.history));
    } catch (error) {
      console.error('Error saving event history:', error);
    }
  }
  
  /**
   * Load event history from localStorage.
   * 
   * @param key Key to load the history from
   * @returns True if successfully loaded, false otherwise
   */
  loadHistory(key: string = 'event_history'): boolean {
    try {
      const data = localStorage.getItem(key);
      if (data) {
        this.history = JSON.parse(data);
        return true;
      }
    } catch (error) {
      console.error('Error loading event history:', error);
    }
    return false;
  }
}

// Create a global event bus instance
export const eventBus = new EventBus();
