/**
 * Detects if the current browser is Safari
 */
const isSafari = (): boolean => {
  const userAgent = navigator.userAgent;
  return /Safari/.test(userAgent) && !/Chrome/.test(userAgent) && !/Chromium/.test(userAgent);
};

/**
 * Opens a PDF URL in a new tab with cross-browser compatibility and Safari popup blocker bypass
 *
 * Browser-specific behavior:
 * - Safari: Uses multiple fallback methods to bypass popup blockers
 * - Chrome/Firefox/Edge: Uses standard window.open which works reliably
 *
 * This approach ensures PDFs open in new tabs for viewing across all major browsers
 */
export const openPdfInNewTab = (url: string): void => {
  // Check if the URL appears to be a PDF
  const isPdf = url.toLowerCase().includes('.pdf') ||
                url.toLowerCase().includes('pdf') ||
                url.includes('application/pdf');

  if (isPdf && isSafari()) {
    // Safari-specific handling for PDFs with multiple fallback methods
    try {
      // Method 1: Try creating a link element and clicking it (most reliable for Safari)
      const link = document.createElement('a');
      link.href = url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';

      // Add the link to the document temporarily
      document.body.appendChild(link);

      // Programmatically click the link
      link.click();

      // Remove the link from the document
      document.body.removeChild(link);

      console.log('Safari: Opened PDF using link click method');
      return;
    } catch (error) {
      console.warn('Safari link click method failed, trying window.open:', error);
    }

    try {
      // Method 2: Try the two-step window.open approach
      const newWindow = window.open('', '_blank', 'noopener,noreferrer');
      if (newWindow) {
        // Set the location after opening the window
        newWindow.location.href = url;
        console.log('Safari: Opened PDF using two-step window.open method');
        return;
      }
    } catch (error) {
      console.warn('Safari two-step method failed, trying direct method:', error);
    }

    try {
      // Method 3: Direct window.open as fallback
      const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
      if (newWindow) {
        console.log('Safari: Opened PDF using direct window.open method');
        return;
      } else {
        console.warn('Safari: All window.open methods failed, likely blocked by popup blocker');
      }
    } catch (error) {
      console.warn('Safari direct method failed:', error);
    }

    // Method 4: Last resort - show user instruction
    alert(`Safari's popup blocker prevented opening the PDF. Please:\n1. Allow popups for this site in Safari settings\n2. Or copy this URL to a new tab: ${url}`);
    return;
  }

  // Standard method for all other browsers (Chrome, Firefox, Edge)
  try {
    const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
    if (!newWindow) {
      console.warn('Popup may have been blocked, trying alternative method');
      // If popup was blocked, try without the window features
      const fallbackWindow = window.open(url, '_blank');
      if (!fallbackWindow) {
        // Show user instruction if all methods fail
        alert(`Your browser's popup blocker prevented opening the PDF. Please:\n1. Allow popups for this site\n2. Or copy this URL to a new tab: ${url}`);
      }
    }
  } catch (error) {
    console.error('Failed to open PDF in new tab:', error);
    // Show user instruction as final fallback
    alert(`Failed to open PDF. Please copy this URL to a new tab: ${url}`);
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
