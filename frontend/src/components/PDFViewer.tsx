import React, { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import { openPdfInNewTab } from '../utils/pdfUtils';

// Set up PDF.js worker - use local file from public directory
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

interface PDFViewerProps {
  pdfUrl: string;
  meetingTitle: string;
}

export const PDFViewer: React.FC<PDFViewerProps> = ({ pdfUrl, meetingTitle: _meetingTitle }) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [documentKey, setDocumentKey] = useState<number>(0);
  const [useIframe, setUseIframe] = useState<boolean>(false);

  // Always use the backend proxy URL (no direct GitHub URLs)
  const fullPdfUrl = pdfUrl.startsWith('http')
    ? pdfUrl
    : `${window.location.origin}${pdfUrl}`;

  // Detect Safari browser
  const isSafari = (): boolean => {
    const userAgent = navigator.userAgent;
    return /Safari/.test(userAgent) && !/Chrome/.test(userAgent) && !/Chromium/.test(userAgent);
  };

  // Reset states when URL changes
  useEffect(() => {
    setUseIframe(false); // Always start with PDF.js enhanced viewer
    setError(null);
    setLoading(true);
    setPageNumber(1);
    setNumPages(0);
  }, [fullPdfUrl]);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
    setLoading(false);
    setError(null);
    console.log('PDF.js loaded successfully');
  }

  function onDocumentLoadError(error: Error) {
    console.error('PDF.js error loading PDF:', error);
    console.error('PDF URL that failed:', fullPdfUrl);
    setError(`PDF.js failed to load: ${error.message}`);
    setLoading(false);
  }

  function changePage(offset: number) {
    setPageNumber(prevPageNumber => prevPageNumber + offset);
  }

  function previousPage() {
    changePage(-1);
  }

  function nextPage() {
    changePage(1);
  }

  // Iframe fallback view
  if (useIframe) {
    return (
      <div className="pdf-viewer">
        <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              📄 PDF Viewer (Simple Mode)
            </span>
            <button
              onClick={() => {
                setUseIframe(false);
                setLoading(true);
                setError(null);
                setDocumentKey(prev => prev + 1); // Force re-render
              }}
              className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded hover:bg-blue-200 transition-colors"
            >
              Try Enhanced Viewer
            </button>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => openPdfInNewTab(fullPdfUrl)}
              className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded hover:bg-green-200 transition-colors"
            >
              Open in New Tab →
            </button>
          </div>
        </div>

        <div className="border border-gray-300 rounded-lg overflow-hidden bg-white relative">
          <iframe
            src={fullPdfUrl}
            className="w-full h-[600px]"
            title="PDF Document"
            onLoad={() => {
              console.log('PDF iframe loaded successfully');
              setLoading(false);
            }}
            onError={() => {
              console.error('PDF iframe failed to load');
              setError('Failed to load PDF in iframe');
              setLoading(false);
            }}
          />
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 z-10">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span className="text-gray-600">Loading PDF...</span>
              </div>
            </div>
          )}
          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-red-50 z-10">
              <div className="text-center p-4">
                <p className="text-red-700 mb-3">{error}</p>
                <button
                  onClick={() => openPdfInNewTab(fullPdfUrl)}
                  className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded hover:bg-blue-200 transition-colors"
                >
                  Open in New Tab →
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // PDF.js enhanced viewer
  return (
    <div className="pdf-viewer">
      <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center space-x-4">
          <button
            type="button"
            disabled={pageNumber <= 1}
            onClick={previousPage}
            className="px-3 py-1 bg-blue-600 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-sm text-gray-600">
            Page {pageNumber} of {numPages || '?'}
          </span>
          <button
            type="button"
            disabled={pageNumber >= numPages}
            onClick={nextPage}
            className="px-3 py-1 bg-blue-600 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => openPdfInNewTab(fullPdfUrl)}
            className="text-sm bg-green-100 text-green-800 px-3 py-1 rounded hover:bg-green-200 transition-colors"
          >
            Open in New Tab →
          </button>
          {isSafari() && (
            <span className="text-xs text-gray-500">
              (Allow popups if blocked)
            </span>
          )}
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="text-gray-600">Loading PDF...</span>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">PDF Loading Error</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => {
                    setError(null);
                    setLoading(true);
                    setDocumentKey(prev => prev + 1); // Force re-render
                  }}
                  className="text-sm bg-red-100 text-red-800 px-3 py-1 rounded hover:bg-red-200 transition-colors"
                >
                  Retry Loading
                </button>
                <button
                  onClick={() => openPdfInNewTab(fullPdfUrl)}
                  className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded hover:bg-blue-200 transition-colors"
                >
                  Open in New Tab →
                </button>
              </div>
              {isSafari() && (
                <p className="mt-2 text-xs text-red-600">
                  <strong>Safari users:</strong> If the PDF doesn't open, please allow popups for this site in Safari → Settings → Websites → Pop-up Windows
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {!error && (
        <div className="border border-gray-300 rounded-lg overflow-hidden">
          <Document
            key={documentKey}
            file={fullPdfUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading=""
          >
            <Page
              pageNumber={pageNumber}
              renderTextLayer={true}
              renderAnnotationLayer={true}
              className="max-w-full"
              width={Math.min(window.innerWidth - 100, 800)}
            />
          </Document>
        </div>
      )}
    </div>
  );
};
