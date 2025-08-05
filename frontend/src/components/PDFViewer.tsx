import React, { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

interface PDFViewerProps {
  pdfUrl: string;
  meetingTitle: string;
}

export const PDFViewer: React.FC<PDFViewerProps> = ({ pdfUrl, meetingTitle: _meetingTitle }) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
    setLoading(false);
    setError(null);
  }

  function onDocumentLoadError(error: Error) {
    console.error('Error loading PDF:', error);
    setError('Failed to load PDF document');
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

  // Construct full URL if relative path
  const fullPdfUrl = pdfUrl.startsWith('http')
    ? pdfUrl
    : `${window.location.origin}/api/v1${pdfUrl.startsWith('/') ? pdfUrl : `/${pdfUrl}`}`;

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
          <span className="text-sm text-gray-700">
            Page {pageNumber || (numPages ? 1 : '--')} of {numPages || '--'}
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
        <a
          href={fullPdfUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
        >
          Open in New Tab →
        </a>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading PDF...</span>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <a
            href={fullPdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-2 inline-block text-red-600 hover:text-red-800 underline"
          >
            Try opening in new tab →
          </a>
        </div>
      )}

      {!error && (
        <div className="border border-gray-300 rounded-lg overflow-hidden">
          <Document
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
            />
          </Document>
        </div>
      )}
    </div>
  );
};
