/**
 * Detects if the current browser is Safari
 */
const isSafari = (): boolean => {
  const userAgent = navigator.userAgent;
  return /Safari/.test(userAgent) && !/Chrome/.test(userAgent) && !/Chromium/.test(userAgent);
};

/**
 * Opens a PDF URL in a new tab with cross-browser compatibility
 *
 * Browser-specific behavior:
 * - Safari: Uses two-step approach (window.open + location.href) to prevent downloads
 * - Chrome/Firefox/Edge: Uses standard window.open which works reliably
 *
 * This approach ensures PDFs open in new tabs across all major browsers
 */
export const openPdfInNewTab = (url: string): void => {
  // Check if the URL appears to be a PDF
  const isPdf = url.toLowerCase().includes('.pdf') ||
                url.toLowerCase().includes('pdf') ||
                url.includes('application/pdf');

  if (isPdf && isSafari()) {
    // Safari-specific handling for PDFs
    try {
      // Method 1: Try the two-step approach for Safari
      const newWindow = window.open('', '_blank', 'noopener,noreferrer');
      if (newWindow) {
        // Set the location after opening the window
        // This helps Safari treat it as navigation rather than a download
        newWindow.location.href = url;
        return;
      }
    } catch (error) {
      console.warn('Safari two-step method failed, falling back to standard method:', error);
    }
  }

  // Standard method for all browsers (Chrome, Firefox, Edge) and Safari fallback
  try {
    const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
    if (!newWindow) {
      console.warn('Popup may have been blocked, trying alternative method');
      // If popup was blocked, try without the window features
      window.open(url, '_blank');
    }
  } catch (error) {
    console.error('Failed to open PDF in new tab:', error);
    // Last resort: try to navigate current window
    window.location.href = url;
  }
};

/**
 * Creates an optimized PDF URL for better browser compatibility
 * Only adds safe parameters that help browsers display PDFs inline
 */
const optimizePdfUrl = (url: string): string => {
  // For now, return the original URL to avoid any potential server compatibility issues
  // The browser-specific handling in openPdfInNewTab should be sufficient
  // Future enhancement: could add #view=FitH anchor for PDF.js compatible viewers

  // Add PDF.js viewer parameters if it's a relative URL (our own PDFs)
  if (!url.startsWith('http') && url.includes('.pdf')) {
    return `${url}#view=FitH`;
  }

  return url;
};

/**
 * Creates a click handler that opens a URL in a new tab with cross-browser compatibility
 */
export const createOpenInNewTabHandler = (url: string) => {
  return (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    // Optimize PDF URLs for better browser handling
    const isPdf = url.toLowerCase().includes('.pdf') ||
                  url.toLowerCase().includes('pdf') ||
                  url.includes('application/pdf');

    const optimizedUrl = isPdf ? optimizePdfUrl(url) : url;
    openPdfInNewTab(optimizedUrl);
  };
};
