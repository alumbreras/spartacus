import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Settings, Info, Zap, Code, Search, Palette, BarChart3 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

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

const API_BASE_URL = 'http://127.0.0.1:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('default');
  const [sessionId, setSessionId] = useState<string>('');
  const [backendStatus, setBackendStatus] = useState<BackendStatus>({ running: false, port: 8000 });
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
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

  const getAgentInfo = (agentType: string) => {
    return AGENT_TYPES.find(agent => agent.id === agentType) || AGENT_TYPES[0];
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-16'}`}>
        <div className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="font-semibold text-gray-900 dark:text-white">Spartacus</h1>
                <p className="text-xs text-gray-500">Desktop</p>
              </div>
            )}
          </div>
        </div>

        <div className="px-4 py-2">
          <button
            onClick={clearChat}
            className="w-full text-left p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-300"
          >
            {sidebarOpen ? 'New Chat' : '✚'}
          </button>
        </div>

        {sidebarOpen && (
          <div className="px-4 py-4">
            <h3 className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">
              Agents
            </h3>
            <div className="space-y-1">
              {AGENT_TYPES.map((agent) => {
                const IconComponent = agent.icon;
                return (
                  <button
                    key={agent.id}
                    onClick={() => setSelectedAgent(agent.id)}
                    className={`w-full text-left p-2 rounded-lg text-sm transition-colors ${
                      selectedAgent === agent.id
                        ? 'bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <IconComponent className="w-4 h-4" />
                      <span>{agent.name}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div className="mt-auto p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${backendStatus.running ? 'bg-green-400' : 'bg-red-400'}`} />
            {sidebarOpen && (
              <span className="text-xs text-gray-500">
                Backend {backendStatus.running ? 'Connected' : 'Disconnected'}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <Settings className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
              
              <div className="flex items-center gap-2">
                {React.createElement(getAgentInfo(selectedAgent).icon, { className: "w-5 h-5 text-blue-600" })}
                <span className="font-medium text-gray-900 dark:text-white">
                  {getAgentInfo(selectedAgent).name} Agent
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className={`px-2 py-1 rounded-full text-xs ${
                backendStatus.running 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                  : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
              }`}>
                {backendStatus.running ? 'Online' : 'Offline'}
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Welcome to Spartacus Desktop
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4 max-w-md">
                Your AI assistant powered by your own agentic library. Choose an agent type and start chatting!
              </p>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Selected: {getAgentInfo(selectedAgent).name} - {getAgentInfo(selectedAgent).description}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                )}
                
                <div className={`max-w-3xl ${message.role === 'user' ? 'order-first' : ''}`}>
                  <div
                    className={`p-4 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white ml-auto'
                        : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <div className="prose prose-sm max-w-none dark:prose-invert">
                      {message.role === 'user' ? (
                        <p className="m-0">{message.content}</p>
                      ) : (
                        <ReactMarkdown
                          components={{
                            code({ node, inline, className, children, ...props }) {
                              const match = /language-(\w+)/.exec(className || '');
                              return !inline && match ? (
                                <SyntaxHighlighter
                                  style={vscDarkPlus}
                                  language={match[1]}
                                  PreTag="div"
                                  {...props}
                                >
                                  {String(children).replace(/\n$/, '')}
                                </SyntaxHighlighter>
                              ) : (
                                <code className={className} {...props}>
                                  {children}
                                </code>
                              );
                            },
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      )}
                    </div>
                    
                    {message.agent_type && message.role === 'assistant' && (
                      <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                        <Info className="w-3 h-3" />
                        <span>{getAgentInfo(message.agent_type).name} Agent</span>
                        {message.tools_used && message.tools_used.length > 0 && (
                          <span>• Tools: {message.tools_used.join(', ')}</span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>

                {message.role === 'user' && (
                  <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                  </div>
                )}
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <span className="ml-2 text-sm text-gray-500">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                disabled={!backendStatus.running}
                className="w-full resize-none border border-gray-300 dark:border-gray-600 rounded-lg p-3 pr-12 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                rows={inputValue.split('\n').length}
              />
              <button
                onClick={sendMessage}
                disabled={!inputValue.trim() || isLoading || !backendStatus.running}
                className="absolute right-2 top-2 p-2 text-blue-600 hover:text-blue-700 disabled:text-gray-400 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              Press Enter to send, Shift+Enter for new line
              {!backendStatus.running && (
                <span className="text-red-500 ml-2">• Backend disconnected</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 