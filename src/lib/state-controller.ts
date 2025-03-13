/**
 * State controller for frontend components.
 * Provides a state machine for tracking agent status.
 */

export enum AgentState {
  IDLE = "idle",
  ANALYZING = "analyzing",
  PLANNING = "planning",
  EXECUTING = "executing",
  REVIEWING = "reviewing",
  ERROR = "error",
  AWAITING_INPUT = "awaiting_input"
}

export class StateTransitionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "StateTransitionError";
  }
}

interface StateHistoryEntry {
  state: AgentState;
  timestamp: string;
  metadata?: Record<string, any>;
}

export class AgentStateController {
  private currentState: AgentState;
  private stateHistory: StateHistoryEntry[];
  private metadata: Record<string, any>;
  
  // Define allowed transitions between states
  private allowedTransitions: Record<AgentState, AgentState[]> = {
    [AgentState.IDLE]: [AgentState.ANALYZING, AgentState.ERROR],
    [AgentState.ANALYZING]: [AgentState.PLANNING, AgentState.ERROR, AgentState.AWAITING_INPUT],
    [AgentState.PLANNING]: [AgentState.EXECUTING, AgentState.ERROR, AgentState.AWAITING_INPUT],
    [AgentState.EXECUTING]: [AgentState.REVIEWING, AgentState.ERROR, AgentState.AWAITING_INPUT],
    [AgentState.REVIEWING]: [AgentState.IDLE, AgentState.ERROR, AgentState.AWAITING_INPUT],
    [AgentState.ERROR]: [AgentState.IDLE],
    [AgentState.AWAITING_INPUT]: [
      AgentState.ANALYZING, 
      AgentState.PLANNING, 
      AgentState.EXECUTING, 
      AgentState.REVIEWING
    ]
  };
  
  /**
   * Create a new state controller.
   * 
   * @param initialState Initial agent state
   */
  constructor(initialState: AgentState = AgentState.IDLE) {
    this.currentState = initialState;
    this.stateHistory = [
      { state: initialState, timestamp: new Date().toISOString() }
    ];
    this.metadata = {};
    
    console.log(`AgentStateController initialized with state: ${initialState}`);
  }
  
  /**
   * Get the current agent state.
   */
  getState(): AgentState {
    return this.currentState;
  }
  
  /**
   * Get the state transition history.
   */
  getStateHistory(): StateHistoryEntry[] {
    return [...this.stateHistory];
  }
  
  /**
   * Check if a transition to the new state is allowed.
   * 
   * @param newState The state to transition to
   * @returns True if the transition is allowed, false otherwise
   */
  canTransitionTo(newState: AgentState): boolean {
    return this.allowedTransitions[this.currentState].includes(newState);
  }
  
  /**
   * Attempt to transition to a new state.
   * 
   * @param newState The state to transition to
   * @param metadata Optional metadata to associate with this state
   * @returns True if the transition was successful
   * @throws StateTransitionError If the transition is not allowed
   */
  setState(newState: AgentState, metadata?: Record<string, any>): boolean {
    if (!this.canTransitionTo(newState)) {
      const errorMsg = `Cannot transition from ${this.currentState} to ${newState}`;
      console.error(errorMsg);
      throw new StateTransitionError(errorMsg);
    }
    
    // Update current state
    this.currentState = newState;
    
    // Update metadata
    if (metadata) {
      this.metadata = { ...this.metadata, ...metadata };
    }
    
    // Record in history
    this.stateHistory.push({
      state: newState,
      timestamp: new Date().toISOString(),
      metadata: metadata || {}
    });
    
    console.log(`State changed to: ${newState}`);
    return true;
  }
  
  /**
   * Get the current metadata.
   */
  getMetadata(): Record<string, any> {
    return { ...this.metadata };
  }
  
  /**
   * Update the metadata without changing state.
   * 
   * @param metadata Metadata to update
   */
  updateMetadata(metadata: Record<string, any>): void {
    this.metadata = { ...this.metadata, ...metadata };
    console.log(`Metadata updated:`, metadata);
  }
  
  /**
   * Clear the state history.
   * 
   * @param keepCurrent Whether to keep the current state in history
   */
  clearHistory(keepCurrent: boolean = true): void {
    if (keepCurrent) {
      this.stateHistory = [this.stateHistory[this.stateHistory.length - 1]];
    } else {
      this.stateHistory = [];
    }
    console.log("State history cleared");
  }
  
  /**
   * Save controller state to localStorage.
   * 
   * @param key Key to save the state under
   */
  saveToLocalStorage(key: string = 'agent_state'): void {
    try {
      const data = {
        currentState: this.currentState,
        stateHistory: this.stateHistory,
        metadata: this.metadata
      };
      
      localStorage.setItem(key, JSON.stringify(data));
      console.log(`State saved to localStorage with key: ${key}`);
    } catch (error) {
      console.error('Error saving state to localStorage:', error);
    }
  }
  
  /**
   * Load controller state from localStorage.
   * 
   * @param key Key to load the state from
   * @returns True if successfully loaded, false otherwise
   */
  loadFromLocalStorage(key: string = 'agent_state'): boolean {
    try {
      const dataStr = localStorage.getItem(key);
      if (!dataStr) return false;
      
      const data = JSON.parse(dataStr);
      
      this.currentState = data.currentState;
      this.stateHistory = data.stateHistory;
      this.metadata = data.metadata;
      
      console.log(`State loaded from localStorage with key: ${key}`);
      return true;
    } catch (error) {
      console.error('Error loading state from localStorage:', error);
      return false;
    }
  }
}

// Create a global state controller instance
export const stateController = new AgentStateController();
