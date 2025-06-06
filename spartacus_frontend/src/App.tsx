import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Settings, Info, Zap, Code, Search, Palette, BarChart3, Copy, RotateCcw, Menu, Plus } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  agent_type?: string;
  tools_used?: string[];
}

interface BackendStatus {
  running: boolean;
  port: number;
}

const AGENT_TYPES = [
  { id: 'default', name: 'General', icon: Bot, description: 'General purpose assistant' },
  { id: 'coding', name: 'Coding', icon: Code, description: 'Programming and development' },
  { id: 'research', name: 'Research', icon: Search, description: 'Research and information gathering' },
  { id: 'analysis', name: 'Analysis', icon: BarChart3, description: 'Data analysis and insights' },
  { id: 'creative', name: 'Creative', icon: Palette, description: 'Creative writing and brainstorming' },
];

const API_BASE_URL = import.meta.env.VITE_SPARTACUS_API_URL || 'http://127.0.0.1:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('default');
  const [sessionId, setSessionId] = useState<string>('');
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({ running: false, port: 8000 });
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // Generate session ID
    setSessionId(`chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
    
    // Check backend status
    checkBackendStatus();
    
    // Focus input
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      setBackendStatus({ running: response.ok, port: 8000 });
    } catch (error) {
      setBackendStatus({ running: false, port: 8000 });
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading || !backendStatus.running) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          agent_type: selectedAgent,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: data.message.id,
        role: 'assistant',
        content: data.message.content,
        timestamp: new Date(data.message.timestamp),
        agent_type: data.message.agent_type,
        tools_used: data.message.tools_used,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `Sorry, I couldn't process your message. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(`chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const getAgentInfo = (agentType: string) => {
    return AGENT_TYPES.find(agent => agent.id === agentType) || AGENT_TYPES[0];
  };

  return (
    <div className="flex h-screen bg-white">
      {/* Sidebar */}
      <div className={`bg-gray-50 border-r border-gray-200 transition-all duration-300 flex flex-col ${sidebarOpen ? 'w-64' : 'w-12'}`}>
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1 rounded-md hover:bg-gray-200 transition-colors"
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
            {sidebarOpen && (
              <button
                onClick={clearChat}
                className="p-1 rounded-md hover:bg-gray-200 transition-colors"
              >
                <Plus className="w-5 h-5 text-gray-600" />
              </button>
            )}
          </div>
          
          {sidebarOpen && (
            <div className="mt-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-gradient-to-r from-orange-400 to-orange-500 rounded-lg flex items-center justify-center">
                  <Zap className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="font-medium text-gray-900">Spartacus</h1>
                  <p className="text-xs text-gray-500">AI Assistant</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Agent Selection */}
        {sidebarOpen && (
          <div className="flex-1 p-4">
            <div className="space-y-1">
              {AGENT_TYPES.map((agent) => {
                const IconComponent = agent.icon;
                return (
                  <button
                    key={agent.id}
                    onClick={() => setSelectedAgent(agent.id)}
                    className={`w-full text-left p-3 rounded-lg text-sm transition-all ${
                      selectedAgent === agent.id
                        ? 'bg-orange-50 text-orange-700 border border-orange-200'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <IconComponent className="w-4 h-4" />
                      <div>
                        <div className="font-medium">{agent.name}</div>
                        <div className="text-xs text-gray-500">{agent.description}</div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Status */}
        <div className="p-4 border-t border-gray-200">
          <div className={`flex items-center gap-2 text-xs ${sidebarOpen ? '' : 'justify-center'}`}>
            <div className={`w-2 h-2 rounded-full ${backendStatus.running ? 'bg-green-500' : 'bg-red-500'}`} />
            {sidebarOpen && (
              <span className="text-gray-500">
                {backendStatus.running ? 'Connected' : 'Disconnected'}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 py-8">
            {messages.length === 0 ? (
              <div className="text-center py-16">
                <div className="w-16 h-16 bg-gradient-to-r from-orange-400 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-2xl font-medium text-gray-900 mb-2">Welcome to Spartacus</h2>
                <p className="text-gray-600 mb-6">Your AI-powered desktop assistant</p>
                <div className="text-left">
                  <p className="text-gray-600 mb-2">Try asking:</p>
                  <div className="space-y-2">
                    <button
                      onClick={() => setInputValue("Write a Python function to calculate fibonacci numbers")}
                      className="block w-full text-left p-3 rounded-lg border border-gray-200 hover:border-orange-300 hover:bg-orange-50 transition-all text-sm"
                    >
                      💻 Write a Python function to calculate fibonacci numbers
                    </button>
                    <button
                      onClick={() => setInputValue("Explain quantum computing in simple terms")}
                      className="block w-full text-left p-3 rounded-lg border border-gray-200 hover:border-orange-300 hover:bg-orange-50 transition-all text-sm"
                    >
                      🔬 Explain quantum computing in simple terms
                    </button>
                    <button
                      onClick={() => setInputValue("Help me brainstorm ideas for a mobile app")}
                      className="block w-full text-left p-3 rounded-lg border border-gray-200 hover:border-orange-300 hover:bg-orange-50 transition-all text-sm"
                    >
                      🎨 Help me brainstorm ideas for a mobile app
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message) => (
                  <div key={message.id} className="group">
                    <div className="flex gap-4">
                      {/* Avatar */}
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        message.role === 'user' 
                          ? 'bg-gray-100' 
                          : 'bg-gradient-to-r from-orange-400 to-orange-500'
                      }`}>
                        {message.role === 'user' ? (
                          <User className="w-4 h-4 text-gray-600" />
                        ) : (
                          <Bot className="w-4 h-4 text-white" />
                        )}
                      </div>

                      {/* Message Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-gray-900">
                            {message.role === 'user' ? 'You' : 'Spartacus'}
                          </span>
                          {message.agent_type && message.agent_type !== 'default' && (
                            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                              {getAgentInfo(message.agent_type).name}
                            </span>
                          )}
                        </div>
                        
                        <div className="prose prose-sm max-w-none">
                          <ReactMarkdown
                            components={{
                              code({ node, className, children, ...props }: any) {
                                const match = /language-(\w+)/.exec(className || '');
                                const isInline = !match;
                                return !isInline ? (
                                  <SyntaxHighlighter
                                    style={oneLight as any}
                                    language={match[1]}
                                    PreTag="div"
                                    className="rounded-lg !bg-gray-50 !border border-gray-200"
                                    {...props}
                                  >
                                    {String(children).replace(/\n$/, '')}
                                  </SyntaxHighlighter>
                                ) : (
                                  <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm" {...props}>
                                    {children}
                                  </code>
                                );
                              },
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>

                        {/* Message Actions */}
                        {message.role === 'assistant' && (
                          <div className="flex items-center gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => copyMessage(message.content)}
                              className="p-1 rounded-md hover:bg-gray-100 transition-colors"
                              title="Copy message"
                            >
                              <Copy className="w-4 h-4 text-gray-500" />
                            </button>
                            <button
                              onClick={() => {
                                // Retry functionality - resend the last user message
                                const lastUserMessage = messages.filter(m => m.role === 'user').pop();
                                if (lastUserMessage) {
                                  setInputValue(lastUserMessage.content);
                                }
                              }}
                              className="p-1 rounded-md hover:bg-gray-100 transition-colors"
                              title="Retry"
                            >
                              <RotateCcw className="w-4 h-4 text-gray-500" />
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-orange-400 to-orange-500 flex items-center justify-center">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 mb-1">Spartacus</div>
                      <div className="flex items-center gap-1">
                        <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse"></div>
                        <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white">
          <div className="max-w-3xl mx-auto p-4">
            <div className="relative">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Message Spartacus..."
                className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-200 focus:border-orange-300 focus:ring-2 focus:ring-orange-100 focus:outline-none resize-none text-gray-900 placeholder-gray-500"
                style={{ minHeight: '52px', maxHeight: '200px' }}
                disabled={!backendStatus.running}
                rows={1}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 200) + 'px';
                }}
              />
              <button
                onClick={sendMessage}
                disabled={!inputValue.trim() || isLoading || !backendStatus.running}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-lg bg-orange-500 hover:bg-orange-600 disabled:bg-gray-200 disabled:cursor-not-allowed transition-colors"
              >
                <Send className="w-4 h-4 text-white" />
              </button>
            </div>
            
            <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
              <div>
                {getAgentInfo(selectedAgent).name} agent selected
              </div>
              <div>
                Press Enter to send, Shift+Enter for new line
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 