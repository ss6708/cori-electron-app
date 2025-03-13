export interface Message {
  role: "user" | "system" | "assistant";
  content: string;
  timestamp: string;
  displayed: boolean;
  thinkingTime?: number;
}

export interface MessageGroup extends Array<Message> {}
