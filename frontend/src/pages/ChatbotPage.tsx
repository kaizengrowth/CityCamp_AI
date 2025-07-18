import React from 'react';

export const ChatbotPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">AI Assistant</h1>
      
      <div className="bg-white rounded-lg shadow h-96 flex flex-col">
        <div className="border-b border-gray-200 p-4">
          <h3 className="text-lg font-semibold">Chat with CityCamp AI</h3>
          <p className="text-gray-600 text-sm">Ask questions about city government, meetings, or policies</p>
        </div>
        
        <div className="flex-1 p-4 overflow-y-auto">
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm">AI</span>
              </div>
              <div className="bg-gray-100 rounded-lg p-3">
                <p className="text-gray-800">Hello! I'm your CityCamp AI assistant. How can I help you today?</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="Type your message..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button className="btn btn-primary">Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}; 