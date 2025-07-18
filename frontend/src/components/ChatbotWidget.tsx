import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { apiRequest, API_ENDPOINTS } from '../config/api';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

// Custom components for markdown rendering
const MarkdownComponents = {
  // Handle links with proper styling and external opening
  a: ({ href, children, ...props }: any) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-600 hover:text-blue-800 underline font-medium"
      {...props}
    >
      {children}
    </a>
  ),
  // Handle paragraphs with proper spacing
  p: ({ children, ...props }: any) => (
    <p className="mb-2 last:mb-0" {...props}>
      {children}
    </p>
  ),
  // Handle lists with proper styling
  ul: ({ children, ...props }: any) => (
    <ul className="list-disc list-inside mb-2 ml-2" {...props}>
      {children}
    </ul>
  ),
  ol: ({ children, ...props }: any) => (
    <ol className="list-decimal list-inside mb-2 ml-2" {...props}>
      {children}
    </ol>
  ),
  li: ({ children, ...props }: any) => (
    <li className="mb-1" {...props}>
      {children}
    </li>
  ),
  // Handle strong/bold text
  strong: ({ children, ...props }: any) => (
    <strong className="font-semibold" {...props}>
      {children}
    </strong>
  ),
  // Handle emphasis/italic text
  em: ({ children, ...props }: any) => (
    <em className="italic" {...props}>
      {children}
    </em>
  ),
  // Handle code blocks
  code: ({ children, ...props }: any) => (
    <code className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono" {...props}>
      {children}
    </code>
  ),
  // Handle blockquotes
  blockquote: ({ children, ...props }: any) => (
    <blockquote className="border-l-4 border-gray-300 pl-4 italic mb-2" {...props}>
      {children}
    </blockquote>
  ),
};

// Utility function to render markdown messages
const renderMarkdownMessage = (text: string): React.ReactNode => {
  if (!text) return null;

  return (
    <ReactMarkdown
      components={MarkdownComponents}
      className="prose prose-sm max-w-none"
    >
      {text}
    </ReactMarkdown>
  );
};

export const ChatbotWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your **CityCamp AI assistant** for Tulsa civic engagement.\n\nI can help you with:\n• 🏛️ City council meetings and agendas\n• 📋 Local campaigns and initiatives\n• 🔔 Setting up notifications\n• 🗳️ Civic participation opportunities\n\nWhat would you like to know about **Tulsa** local government?",
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    const messageText = inputValue;
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Prepare conversation history for API
      const conversationHistory = messages.map(msg => ({
        text: msg.text,
        sender: msg.sender
      }));

      // Call the API
      const response = await apiRequest<{response: string; success: boolean; error?: string}>(
        API_ENDPOINTS.chatbot,
        {
          method: 'POST',
          body: JSON.stringify({
            message: messageText,
            conversation_history: conversationHistory
          }),
        }
      );

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error getting AI response:', error);

      // Fallback to local response if API fails
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: getBotResponse(messageText),
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const getBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();

    // Check if the question is about Tulsa - if not, provide guardrail response
    if (!input.includes('tulsa') && !input.includes('city') && !input.includes('council') &&
        !input.includes('meeting') && !input.includes('campaign') && !input.includes('civic') &&
        !input.includes('government') && !input.includes('local') && !input.includes('mayor') &&
        !input.includes('election') && !input.includes('petition') && !input.includes('notification')) {
      return "I'm specifically designed to help with **Tulsa, Oklahoma** civic engagement and local government matters.\n\nI can assist you with:\n• City council meetings and agendas\n• Local campaigns and initiatives\n• Civic participation opportunities\n• Government services and information\n\nPlease ask me about **Tulsa** local government topics!";
    }

    if (input.includes('meeting') || input.includes('council')) {
      return "I can help you find information about **Tulsa City Council meetings**!\n\nYou can:\n• View upcoming meetings and agendas on the [Meetings page](/meetings)\n• Read past meeting minutes and summaries\n• Get notifications about meetings that interest you\n\nFor official information, visit the [City of Tulsa website](https://www.cityoftulsa.org/government/city-council/)\n\nWhat specific meeting information are you looking for?";
    }

    if (input.includes('campaign') || input.includes('petition')) {
      return "**CityCamp AI** helps you stay informed about local Tulsa campaigns and petitions.\n\nCheck out the [Campaigns page](/campaigns) to:\n• See active initiatives in Tulsa\n• Learn about local ballot measures\n• Find ways to get involved in your community\n\nIs there a specific **Tulsa** campaign or issue you're interested in?";
    }

    if (input.includes('notification') || input.includes('alert')) {
      return "You can set up **personalized notifications** for Tulsa civic activities!\n\nGo to your [Profile settings](/profile) to:\n• Get alerts about upcoming meetings\n• Receive updates on campaigns you care about\n• Set preferences for topics that matter to you\n\nWould you like help setting up notifications?";
    }

    if (input.includes('hello') || input.includes('hi')) {
      return "Hello! I'm here to help you stay engaged with **Tulsa local government**.\n\nYou can ask me about:\n• City council meetings and agendas\n• Local campaigns and initiatives\n• Civic participation opportunities\n• Government services and information\n\nWhat would you like to know about **Tulsa**?";
    }

    return "I'm here to help you stay informed about **Tulsa local government** activities.\n\nYou can ask me about:\n• City council meetings and agendas\n• Local campaigns and initiatives\n• Civic participation opportunities\n• Using the CityCamp AI platform\n\nFor official information, visit the [City of Tulsa website](https://www.cityoftulsa.org/)\n\nWhat would you like to know about **Tulsa**?";
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Chat Widget */}
      {isOpen && (
        <div className="mb-4 w-80 h-[32rem] bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col">
          {/* Header */}
          <div className="bg-primary-600 text-white p-4 rounded-t-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-bold">AI</span>
                </div>
                <div>
                  <h3 className="font-semibold">CityCamp AI Assistant</h3>
                  <p className="text-xs text-primary-100">Ask me about Tulsa local government</p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:text-primary-100 transition-colors"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.sender === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-white text-gray-800 border border-gray-200'
                    }`}
                  >
                    <div className="text-sm">
                      {message.sender === 'bot' ? renderMarkdownMessage(message.text) : message.text}
                    </div>
                    <p className={`text-xs mt-2 ${
                      message.sender === 'user' ? 'text-primary-100' : 'text-gray-500'
                    }`}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-white text-gray-800 border border-gray-200 px-4 py-2 rounded-lg">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200 bg-white rounded-b-lg">
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about Tulsa local government..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isTyping}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-primary-600 hover:bg-primary-700 text-white p-4 rounded-full shadow-lg transition-colors"
      >
        {isOpen ? (
          <span className="text-xl">✕</span>
        ) : (
          <span className="text-xl">💬</span>
        )}
      </button>
    </div>
  );
};
