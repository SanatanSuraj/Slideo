"use client";
import React, { useCallback, useEffect } from "react";
import {
  ChevronLeft,
  ChevronRight,
  X,
  Minimize2,
  Maximize2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Slide } from "../types/slide";
import { useTemplateLayouts } from "../hooks/useTemplateLayouts";


interface PresentationModeProps {
  slides: Slide[];
  currentSlide: number;

  isFullscreen: boolean;
  onFullscreenToggle: () => void;
  onExit: () => void;
  onSlideChange: (slideNumber: number) => void;
}

const PresentationMode: React.FC<PresentationModeProps> = ({

  slides,
  currentSlide,

  isFullscreen,
  onFullscreenToggle,
  onExit,
  onSlideChange,

}) => {
  const { renderSlideContent } = useTemplateLayouts();

  // Modify the handleKeyPress to prevent default behavior
  const handleKeyPress = useCallback(
    (event: KeyboardEvent) => {
      event.preventDefault(); // Prevent default scroll behavior

      switch (event.key) {
        case "ArrowRight":
        case "ArrowDown":
        case " ": // Space key
          if (slides && currentSlide < slides.length - 1) {
            onSlideChange(currentSlide + 1);
          }
          break;
        case "ArrowLeft":
        case "ArrowUp":
          if (currentSlide > 0) {
            onSlideChange(currentSlide - 1);
          }
          break;
        case "Escape":
          onExit();
          break;
        case "f":
        case "F":
          onFullscreenToggle();
          break;
      }
    },
    [currentSlide, slides?.length, onSlideChange, onExit, onFullscreenToggle]
  );

  // Add both keydown and keyup listeners
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Prevent default behavior for arrow keys and space
      if (
        ["ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown", " "].includes(e.key)
      ) {
        e.preventDefault();
      }
      handleKeyPress(e);
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyPress]);

  // Add click handlers for the slide area
  const handleSlideClick = (e: React.MouseEvent) => {
    // Don't trigger navigation if clicking on controls
    if ((e.target as HTMLElement).closest(".presentation-controls")) {
      return;
    }

    const clickX = e.clientX;
    const windowWidth = window.innerWidth;

    if (clickX < windowWidth / 3) {
      if (currentSlide > 0) {
        onSlideChange(currentSlide - 1);
      }
    } else if (clickX > (windowWidth * 2) / 3) {
      if (slides && currentSlide < slides.length - 1) {
        onSlideChange(currentSlide + 1);
      }
    }
  };

  // Handle Escape key separately
  useEffect(() => {
    const handleEscKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isFullscreen) {
        onFullscreenToggle(); // Just toggle fullscreen, don't exit presentation
      }
    };

    document.addEventListener("keydown", handleEscKey);
    return () => document.removeEventListener("keydown", handleEscKey);
  }, [isFullscreen, onFullscreenToggle]);

  // Safety check for slides - moved after all hooks
  if (!slides || !Array.isArray(slides) || slides.length === 0) {
    return (
      <div className="fixed inset-0 bg-black flex items-center justify-center">
        <div className="text-white text-center">
          <h2 className="text-2xl font-bold mb-4">No Slides Available</h2>
          <p className="text-gray-300 mb-6">The presentation doesn't have any slides to display.</p>
          <Button onClick={onExit} variant="outline" className="text-white border-white hover:bg-white hover:text-black">
            Exit Presentation
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div
      className="fixed inset-0 bg-black flex flex-col"
      tabIndex={0}
      onClick={handleSlideClick}
    >
      {/* Controls - Only show when not in fullscreen */}
      {!isFullscreen && (
        <>
          <div className="presentation-controls absolute top-4 right-4 flex items-center gap-2 z-50">
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                onFullscreenToggle();
              }}
              className="text-white hover:bg-white/20"
            >
              {isFullscreen ? (
                <Minimize2 className="h-5 w-5" />
              ) : (
                <Maximize2 className="h-5 w-5" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                onExit();
              }}
              className="text-white hover:bg-white/20"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          <div className="presentation-controls absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-4 z-50">
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                onSlideChange(currentSlide - 1);
              }}
              disabled={currentSlide === 0}
              className="text-white hover:bg-white/20"
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            <span className="text-white">
              {currentSlide + 1} / {slides?.length || 0}
            </span>
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                onSlideChange(currentSlide + 1);
              }}
              disabled={!slides || currentSlide === slides.length - 1}
              className="text-white hover:bg-white/20"
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
          </div>
        </>
      )}

      {/* Current Slide */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div
          className={`w-full max-w-[1280px] scale-110 aspect-video slide-theme slide-container border rounded-sm font-inter shadow-lg bg-white`}
        >
          {slides[currentSlide] &&
            renderSlideContent(slides[currentSlide], false)}
        </div>
      </div>
    </div>
  );
};

export default PresentationMode;
