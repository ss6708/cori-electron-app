"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable"
import {
  TechHomeIcon,
  TechPlusIcon,
  TechSearchIcon,
  TechHistoryIcon,
  TechBookmarkIcon,
  TechHelpIcon,
  TechSettingsIcon,
  TechSpreadsheetIcon,
  TechSpreadsheetLargeIcon,
  TechArrowUpIcon,
  TechMaximizeIcon,
} from "./components/tech-icons"
import { Message, MessageGroup } from "./types/message"
import { sendMessageToAI } from "./lib/api"

// Helper function to group messages by time
const groupMessagesByTime = (messages: Message[]): MessageGroup[] => {
  const groups: MessageGroup[] = []
  let currentGroup: Message[] = []

  messages.forEach((message, index) => {
    if (index === 0) {
      currentGroup.push(message)
    } else {
      // Group messages that are within 5 minutes of each other
      const prevTime = new Date(messages[index - 1].timestamp || Date.now())
      const currTime = new Date(message.timestamp || Date.now())
      const diffInMinutes = (currTime.getTime() - prevTime.getTime()) / (1000 * 60)

      if (diffInMinutes < 5) {
        currentGroup.push(message)
      } else {
        groups.push([...currentGroup])
        currentGroup = [message]
      }
    }
  })

  if (currentGroup.length > 0) {
    groups.push(currentGroup)
  }

  return groups
}

export default function ExcelAgentUI() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "system",
      content: "Hi shreya, I can help you analyze and modify your Excel models. What would you like to work on?",
      timestamp: "2023-05-10T09:30:00",
      displayed: true, // Add this to indicate the message is fully displayed
    },
    {
      role: "user",
      content:
        "I went through and found some missing images that I have added to the dir data\\images. now we have complete images and json annotations for all images.",
      timestamp: "2023-05-10T09:31:00",
      displayed: true,
    },
    {
      role: "system",
      content:
        "I'll update the viewer to remove bounding_box_simple objects and only use the vertex-based bounding_box format. I'll then regenerate the viewer with all images.",
      timestamp: "2023-05-10T09:32:00",
      displayed: true,
    },
    {
      role: "user",
      content: "Can you help me analyze the sensitivity of our financial model to changes in interest rates?",
      timestamp: "2023-05-10T09:45:00",
      displayed: true,
    },
    {
      role: "system",
      content:
        "Of course. I'll run a sensitivity analysis on your financial model with respect to interest rate changes. Which specific variables would you like me to focus on?",
      timestamp: "2023-05-10T09:46:00",
      displayed: true,
    },
  ])

  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [thinkingStartTime, setThinkingStartTime] = useState<number | null>(null)
  const [thinkingDuration, setThinkingDuration] = useState<number | null>(null)

  // Add state for typewriter effect
  const [displayedText, setDisplayedText] = useState<Record<number, string>>({})
  const [activeTypingIndex, setActiveTypingIndex] = useState<number | null>(null)

  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const messageEndRef = useRef<HTMLDivElement>(null)

  // Auto-resize textarea as content grows
  useEffect(() => {
    if (textareaRef.current) {
      // Reset height to auto to get the correct scrollHeight
      textareaRef.current.style.height = "40px"
      // Set the height to scrollHeight to expand the textarea
      const scrollHeight = textareaRef.current.scrollHeight
      textareaRef.current.style.height = `${Math.min(scrollHeight, 120)}px`
    }
  }, [input])

  // Scroll to bottom when new messages are added or text is being typed
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, displayedText])

  // Typewriter effect for system messages
  useEffect(() => {
    // Find the first system message that hasn't been fully displayed yet
    const messageIndex = messages.findIndex((msg, index) => msg.role === "system" && !msg.displayed)

    if (messageIndex !== -1) {
      const message = messages[messageIndex]
      setActiveTypingIndex(messageIndex)

      let charIndex = 0
      const fullText = message.content
      const typingSpeed = 30 // milliseconds per character

      // Start with an empty string
      setDisplayedText((prev) => ({
        ...prev,
        [messageIndex]: "",
      }))

      // Function to add one character at a time
      const typeNextChar = () => {
        if (charIndex < fullText.length) {
          setDisplayedText((prev) => ({
            ...prev,
            [messageIndex]: fullText.substring(0, charIndex + 1),
          }))
          charIndex++
          setTimeout(typeNextChar, typingSpeed)
        } else {
          // Mark message as fully displayed
          setMessages((prev) => prev.map((msg, idx) => (idx === messageIndex ? { ...msg, displayed: true } : msg)))
          setActiveTypingIndex(null)
        }
      }

      // Start typing
      typeNextChar()
    }
  }, [messages])

  // Replace the existing useEffect for typing with this updated version
  useEffect(() => {
    if (isTyping) {
      // If we just started typing, record the start time
      if (!thinkingStartTime) {
        setThinkingStartTime(Date.now())
      }
      
      // We no longer need this timeout as we're waiting for the actual API response
      // The typing indicator will be hidden when the response is received
    }
  }, [isTyping, thinkingStartTime])

  // Update the handleSend function to send messages to OpenAI
  const handleSend = async () => {
    console.log("handleSend called")
    if (input.trim()) {
      // Create new user message
      const userMessage: Message = {
        role: "user",
        content: input,
        timestamp: new Date().toISOString(),
        displayed: true, // User messages are displayed immediately
      }
      
      console.log("User message:", userMessage)
      
      // Add user message to state
      setMessages([...messages, userMessage])
      setInput("")
      
      // Show typing indicator and reset thinking time
      setThinkingStartTime(null)
      setThinkingDuration(null)
      setIsTyping(true)
      
      try {
        console.log("Sending message to OpenAI API...")
        // Send messages to OpenAI API
        const aiResponse = await sendMessageToAI([...messages, userMessage])
        console.log("Received AI response:", aiResponse)
        
        // When response is received, hide typing indicator
        setIsTyping(false)
        
        // Add AI response to messages
        setMessages((prev) => [...prev, aiResponse])
      } catch (error) {
        console.error("Error getting AI response:", error)
        setIsTyping(false)
        
        // Add error message
        setMessages((prev) => [
          ...prev,
          {
            role: "system",
            content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : String(error)}`,
            timestamp: new Date().toISOString(),
            displayed: false,
          },
        ])
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const messageGroups = groupMessagesByTime(messages)

  return (
    <div className="flex h-screen bg-[#0a0f1a] text-gray-200 font-quantico font-thin animate-gradient">
      {/* Collapsed Sidebar with Icons */}
      <div className="w-16 border-r border-[#ffffff0f] flex flex-col items-center py-4 bg-[#1a2035]/20 backdrop-blur-md">
        <div className="mb-6">
          {/* For the main app icon at the top */}
          <div className="h-10 w-10 rounded-full flex items-center justify-center bg-blue-600/30 backdrop-blur-sm border border-[#ffffff0f] shadow-[0_0_15px_rgba(59,130,246,0.3)] animate-pulse">
            <TechSpreadsheetIcon />
          </div>
        </div>

        <div className="flex flex-col items-center gap-4 flex-1">
          <div className="p-1 rounded-lg bg-[#1a2035]/20 backdrop-blur-sm border border-[#ffffff0f] gradient-border transition-all duration-300 hover:bg-[#1a2035]/40">
            {/* For the sidebar icons, make them slightly larger */}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-md text-gray-400 hover:text-white hover:bg-[#ffffff10] transition-colors"
            >
              <TechHomeIcon />
            </Button>
          </div>

          <div className="p-1 rounded-lg bg-[#1a2035]/20 backdrop-blur-sm border border-[#ffffff0f] gradient-border transition-all duration-300 hover:bg-[#1a2035]/40">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-md text-gray-400 hover:text-white hover:bg-[#ffffff10] transition-colors"
            >
              <TechPlusIcon />
            </Button>
          </div>

          <div className="p-1 rounded-lg bg-[#1a2035]/20 backdrop-blur-sm border border-[#ffffff0f] gradient-border transition-all duration-300 hover:bg-[#1a2035]/40">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-md text-gray-400 hover:text-white hover:bg-[#ffffff10] transition-colors"
            >
              <TechSearchIcon />
            </Button>
          </div>

          <div className="p-1 rounded-lg bg-[#1a2035]/20 backdrop-blur-sm border border-[#ffffff0f] gradient-border transition-all duration-300 hover:bg-[#1a2035]/40">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-md text-gray-400 hover:text-white hover:bg-[#ffffff10] transition-colors"
            >
              <TechHistoryIcon />
            </Button>
          </div>

          <div className="p-1 rounded-lg bg-[#1a2035]/20 backdrop-blur-sm border border-[#ffffff0f] gradient-border transition-all duration-300 hover:bg-[#1a2035]/40">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-md text-gray-400 hover:text-white hover:bg-[#ffffff10] transition-colors"
            >
              <TechBookmarkIcon />
            </Button>
          </div>
        </div>

        <div className="mt-auto flex flex-col items-center gap-4">
          <div className="p-1 rounded-lg bg-[#1a2035]/20 backdrop-blur-sm border border-[#ffffff0f] gradient-border transition-all duration-300 hover:bg-[#1a2035]/40">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-md text-gray-400 hover:text-white hover:bg-[#ffffff10] transition-colors"
            >
              <TechHelpIcon />
            </Button>
          </div>

          <div className="p-1 rounded-lg bg-[#1a2035]/20 backdrop-blur-sm border border-[#ffffff0f] gradient-border transition-all duration-300 hover:bg-[#1a2035]/40">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 rounded-md text-gray-400 hover:text-white hover:bg-[#ffffff10] transition-colors"
            >
              <TechSettingsIcon />
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content - Split Panel View */}
      <div className="flex-1">
        {/* Top Navigation */}
        <div className="border-b border-[#ffffff0f] p-3 flex items-center justify-between bg-[#1a2035]/20 backdrop-blur-md noise-texture">
          <div className="flex items-center gap-2">
            <h1 className="font-quantico font-thin text-lg tracking-wide text-gradient">Fine-tune Excel Model</h1>
            <div className="bg-[#1a2035]/40 backdrop-blur-sm text-xs px-2 py-0.5 rounded-md ml-2 border border-[#ffffff0f] gradient-border">
              4 Changes from v12
            </div>
            <div className="bg-yellow-600/40 backdrop-blur-sm text-xs px-2 py-0.5 rounded-md ml-2 border border-[#ffffff0f] gradient-border">
              2 PENDING
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="bg-[#1a2035]/30 border-[#ffffff0f] text-gray-200 hover:bg-[#ffffff10] backdrop-blur-sm transition-all duration-300 hover:scale-105"
            >
              Quit
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="bg-[#1a2035]/30 border-[#ffffff0f] text-gray-200 hover:bg-[#ffffff10] backdrop-blur-sm transition-all duration-300 hover:scale-105"
            >
              Diff
            </Button>
            <Button
              size="sm"
              className="bg-blue-600/30 hover:bg-blue-600/50 text-white backdrop-blur-sm border border-[#ffffff1a] px-4 shadow-[0_0_15px_rgba(59,130,246,0.3)] transition-all duration-300 hover:shadow-[0_0_20px_rgba(59,130,246,0.5)] hover:scale-105"
            >
              Save as New Version
            </Button>
          </div>
        </div>

        {/* Split Panel View with Custom Resizer */}
        <ResizablePanelGroup direction="horizontal" className="[&>div[data-panel-id]]:h-[calc(100vh-57px)]">
          {/* Chat Panel */}
          <ResizablePanel defaultSize={40} minSize={30}>
            <div className="flex flex-col h-full p-4">
              {/* Chat Messages - Starting directly with message history */}
              <div className="flex-1 rounded-lg overflow-hidden relative backdrop-blur-md bg-[#1a2035]/30 border border-[#ffffff0f] shadow-[inset_0_0_20px_rgba(0,0,0,0.2)] before:absolute before:inset-0 before:bg-gradient-to-b before:from-[#ffffff08] before:to-transparent before:pointer-events-none gradient-border noise-texture">
                <ScrollArea className="h-full px-4 pt-4 pb-4 custom-scrollbar" ref={scrollAreaRef}>
                  {messageGroups.map((group, groupIndex) => (
                    <div key={groupIndex} className="mb-8">
                      {/* Time divider */}
                      {groupIndex > 0 && (
                        <div className="flex items-center my-6">
                          <div className="flex-grow h-px bg-gray-700/30"></div>
                          <div className="mx-4 text-xs text-gray-500">
                            {new Date(group[0].timestamp).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                              hour12: true,
                            })}
                          </div>
                          <div className="flex-grow h-px bg-gray-700/30"></div>
                        </div>
                      )}

                      {/* Messages in this group */}
                      {group.map((message, index) => {
                        // Get the global index of this message in the messages array
                        const globalIndex = messages.findIndex(
                          (m) => m.timestamp === message.timestamp && m.content === message.content,
                        )

                        return (
                          <div
                            key={`${groupIndex}-${index}`}
                            className={`mb-4 transition-all duration-300 hover:translate-x-1 ${
                              message.role === "system" ? "hover:bg-blue-900/5" : "hover:bg-gray-700/5"
                            } rounded-md p-1`}
                          >
                            <div className="flex items-center gap-2 mb-1">
                              {message.role === "system" ? (
                                <>
                                  <div className="h-5 w-5 bg-blue-600/80 rounded flex items-center justify-center text-xs backdrop-blur-sm shadow-[0_0_10px_rgba(59,130,246,0.3)] transition-all duration-300 hover:shadow-[0_0_15px_rgba(59,130,246,0.5)]">
                                    C
                                  </div>
                                  <span className="text-sm tracking-wide">Cori</span>
                                </>
                              ) : (
                                <>
                                  <div className="h-5 w-5 bg-gray-600/50 rounded flex items-center justify-center text-xs backdrop-blur-sm transition-all duration-300 hover:bg-gray-600/70">
                                    SH
                                  </div>
                                  <span className="text-sm tracking-wide">shreya</span>
                                </>
                              )}
                              <span className="text-xs text-gray-500">
                                {new Date(message.timestamp).toLocaleTimeString([], {
                                  hour: "2-digit",
                                  minute: "2-digit",
                                })}
                              </span>
                            </div>
                            <div className="pl-7">
                              {/* Apply typewriter effect for system messages that are being typed */}
                              {message.role === "system" && !message.displayed ? (
                                <p className="text-xs text-gray-200/90 leading-relaxed font-mono font-normal tracking-tight">
                                  <span
                                    className={`typewriter-text ${activeTypingIndex !== globalIndex ? "complete" : ""}`}
                                  >
                                    {displayedText[globalIndex] || ""}
                                  </span>
                                </p>
                              ) : (
                                <p className="text-xs text-gray-200/90 leading-relaxed font-mono font-normal tracking-tight">
                                  {message.content}
                                </p>
                              )}
                              {message.thinkingTime && (
                                <div className="mt-1 text-[10px] text-blue-400/60 font-mono">
                                  Thought for {message.thinkingTime} {message.thinkingTime === 1 ? "second" : "seconds"}
                                </div>
                              )}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  ))}

                  {/* Updated thinking indicator with italicized text */}
                  {isTyping && (
                    <div className="mb-6">
                      <div className="flex items-center gap-2 mb-1">
                        <div className="h-5 w-5 bg-blue-600/80 rounded flex items-center justify-center text-xs backdrop-blur-sm shadow-[0_0_10px_rgba(59,130,246,0.3)]">
                          C
                        </div>
                        <span className="text-sm">Cori</span>
                        <span className="text-xs text-gray-500">
                          {new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                        </span>
                      </div>
                      <div className="pl-7">
                        <div className="thinking-text py-1 px-2 rounded-md bg-blue-900/10 inline-block">
                          <span className="text-xs font-mono mask-scan-text">Cori is thinking</span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messageEndRef} />
                </ScrollArea>
              </div>

              {/* Chat Input - Auto-expanding Textarea */}
              <div className="mt-4">
                <div className="relative">
                  <Textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Send a message..."
                    className="bg-[#1a2035]/30 border-[#ffffff0f] pr-10 text-sm backdrop-blur-md shadow-[inset_0_0_20px_rgba(0,0,0,0.1)] placeholder:text-gray-  pr-10 text-sm backdrop-blur-md shadow-[inset_0_0_20px_rgba(0,0,0,0.1)] placeholder:text-gray-500 min-h-[40px] max-h-[120px] resize-none py-2 px-3 transition-all duration-300 focus:shadow-[0_0_15px_rgba(59,130,246,0.2)] gradient-border"
                    style={{ overflow: "hidden" }}
                  />
                  <Button
                    onClick={handleSend}
                    className="absolute right-1 top-1 h-7 w-7 p-0 bg-blue-600/80 hover:bg-blue-700/80 text-white rounded-md backdrop-blur-sm shadow-[0_0_10px_rgba(59,130,246,0.3)] transition-all duration-300 hover:shadow-[0_0_15px_rgba(59,130,246,0.5)] disabled:opacity-50 disabled:hover:bg-blue-600/80 disabled:hover:shadow-[0_0_10px_rgba(59,130,246,0.3)]"
                    disabled={!input.trim()}
                  >
                    <TechArrowUpIcon />
                  </Button>
                </div>
              </div>
            </div>
          </ResizablePanel>

          {/* Custom Resizer - Lighter grey with no handle */}
          <div className="w-px bg-gray-700/30 relative group backdrop-blur-sm hover:bg-blue-700/20 transition-colors duration-300">
            <div className="absolute inset-y-0 left-1/2 w-4 -translate-x-1/2 cursor-col-resize" />
          </div>

          {/* Excel View Panel */}
          <ResizablePanel defaultSize={60}>
            <div className="flex flex-col h-full p-4">
              {/* Excel Content */}
              <div className="flex-1 rounded-lg overflow-hidden relative backdrop-blur-md bg-[#1a2035]/30 border border-[#ffffff0f] shadow-[inset_0_0_20px_rgba(0,0,0,0.2)] before:absolute before:inset-0 before:bg-gradient-to-b before:from-[#ffffff08] before:to-transparent before:pointer-events-none gradient-border noise-texture">
                {/* Excel Header */}
                <div className="py-1.5 px-3 border-b border-[#ffffff0f] flex items-center justify-between bg-[#ffffff05]">
                  <div className="flex items-center gap-1.5">
                    <TechSpreadsheetIcon />
                    <span className="text-xs text-gray-200/90 tracking-wide">Financial Model.xlsx</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 text-gray-400/90 hover:text-gray-300 transition-all duration-300 hover:bg-[#ffffff10]"
                  >
                    <TechMaximizeIcon />
                  </Button>
                </div>

                {/* Empty Browser-Style Content Area */}
                <div className="flex flex-col items-center justify-center h-full p-6 text-center">
                  <div className="w-16 h-16 mb-4 text-blue-400/70 opacity-70 animate-float">
                    <TechSpreadsheetLargeIcon />
                  </div>
                  <h3 className="text-lg font-thin mb-2 text-gray-300/90 tracking-wide text-gradient">Excel Viewer</h3>
                  <p className="text-sm text-gray-400/80 max-w-md font-mono">
                    This area will display your Excel model in a browser view.
                  </p>
                  <div className="mt-6 p-3 bg-blue-900/10 rounded-lg backdrop-blur-sm border border-blue-500/20 gradient-border transition-all duration-300 hover:bg-blue-900/20">
                    <p className="text-xs text-blue-300/90">Ready to analyze financial data</p>
                  </div>
                </div>
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  )
}

