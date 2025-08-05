const React = require('react');

// Mock react-pdf components
const Document = ({ children, onLoadSuccess, onLoadError, ...props }) => {
  // Simulate successful document load after a brief delay
  React.useEffect(() => {
    if (onLoadSuccess) {
      setTimeout(() => {
        onLoadSuccess({ numPages: 3 });
      }, 100);
    }
  }, [onLoadSuccess]);

  return React.createElement('div', {
    'data-testid': 'pdf-document',
    ...props
  }, children);
};

const Page = ({ pageNumber, ...props }) => {
  return React.createElement('div', {
    'data-testid': 'pdf-page',
    'data-page-number': pageNumber,
    ...props
  }, `Page ${pageNumber}`);
};

// Mock pdfjs object
const pdfjs = {
  GlobalWorkerOptions: {
    workerSrc: 'mock-worker-src'
  }
};

module.exports = {
  Document,
  Page,
  pdfjs
};
