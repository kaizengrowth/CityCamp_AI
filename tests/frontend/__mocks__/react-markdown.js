const React = require('react');

// Mock react-markdown component
const ReactMarkdown = ({ children }) => {
  return React.createElement('div', { 'data-testid': 'react-markdown' }, children);
};

module.exports = ReactMarkdown;
