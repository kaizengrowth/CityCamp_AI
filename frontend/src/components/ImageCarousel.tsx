import React, { useState } from 'react';

interface ImageCarouselProps {
  images: string[];
  title?: string;
}

export const ImageCarousel: React.FC<ImageCarouselProps> = ({ images, title = "Meeting Images" }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!images || images.length === 0) {
    return null;
  }

  const goToPrevious = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? images.length - 1 : prevIndex - 1
    );
  };

  const goToNext = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === images.length - 1 ? 0 : prevIndex + 1
    );
  };

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'ArrowLeft') {
      goToPrevious();
    } else if (event.key === 'ArrowRight') {
      goToNext();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-4 border-b border-gray-200">
        <h4 className="text-lg font-medium text-brand-dark-blue flex items-center">
          📄 {title}
          <span className="ml-2 text-sm font-normal text-gray-500">
            ({currentIndex + 1} of {images.length})
          </span>
        </h4>
      </div>

      <div
        className="relative bg-gray-50"
        onKeyDown={handleKeyDown}
        tabIndex={0}
      >
        {/* Main Image Display */}
        <div className="relative h-96 flex items-center justify-center">
          <img
            src={`/api/v1/meeting-images/${images[currentIndex]}`}
            alt={`Page ${currentIndex + 1}`}
            className="max-h-full max-w-full object-contain shadow-lg"
            onError={(e) => {
              console.error('Image failed to load:', images[currentIndex]);
              e.currentTarget.src = '/placeholder-image.png';
            }}
          />

          {/* Navigation Arrows */}
          {images.length > 1 && (
            <>
              <button
                onClick={goToPrevious}
                className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white/90 hover:bg-white text-gray-700 hover:text-brand-dark-blue rounded-full p-2 shadow-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-brand-yellow"
                aria-label="Previous image"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              <button
                onClick={goToNext}
                className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white/90 hover:bg-white text-gray-700 hover:text-brand-dark-blue rounded-full p-2 shadow-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-brand-yellow"
                aria-label="Next image"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </>
          )}
        </div>

        {/* Thumbnail Navigation */}
        {images.length > 1 && (
          <div className="p-4 bg-gray-100 border-t border-gray-200">
            <div className="flex space-x-2 overflow-x-auto pb-2">
              {images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => goToSlide(index)}
                  className={`flex-shrink-0 w-16 h-12 rounded border-2 overflow-hidden transition-all duration-200 ${
                    index === currentIndex
                      ? 'border-brand-yellow shadow-md'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                  aria-label={`Go to page ${index + 1}`}
                >
                  <img
                    src={`/api/v1/meeting-images/${image}`}
                    alt={`Page ${index + 1} thumbnail`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.src = '/placeholder-image.png';
                    }}
                  />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Keyboard Navigation Hint */}
        {images.length > 1 && (
          <div className="px-4 py-2 bg-gray-50 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              Use ← → arrow keys or click thumbnails to navigate
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
