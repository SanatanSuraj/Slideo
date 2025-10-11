"use client";
import React, {  useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { RootState } from "@/store/store";
import { Skeleton } from "@/components/ui/skeleton";
import PresentationMode from "../../components/PresentationMode";
import SidePanel from "./SidePanel";
import SlideContent from "./SlideContent";
import Header from "./Header";
import { Button } from "@/components/ui/button";
import { usePathname } from "next/navigation";
import { trackEvent, MixpanelEvent } from "@/utils/mixpanel";
import { AlertCircle, Loader2 } from "lucide-react";
import { toast } from "sonner";
import Help from "./Help";
import {
  usePresentationStreaming,
  usePresentationData,
  useFinalPresentationData,
  usePresentationNavigation,
  useAutoSave,
} from "../hooks";
import { PresentationPageProps } from "../types";
import LoadingState from "./LoadingState";
import { useLayout } from "../../context/LayoutContext";
import { useFontLoader } from "../../hooks/useFontLoader";
import { usePresentationUndoRedo } from "../hooks/PresentationUndoRedo";
import { SavingIndicator } from "./SavingIndicator";
const PresentationPage: React.FC<PresentationPageProps> = ({
  presentation_id,
}) => {
  const pathname = usePathname();
  // State management
  const [loading, setLoading] = useState(true);
  const [selectedSlide, setSelectedSlide] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [error, setError] = useState(false);
  const [isMobilePanelOpen, setIsMobilePanelOpen] = useState(false);
  const {getCustomTemplateFonts} = useLayout();
 
  const { presentationData, isStreaming, outlines, isSaving: isAutoSaving, isSaved } = useSelector(
    (state: RootState) => state.presentationGeneration
  );

  // Auto-save functionality
  const { isSaving, manualSave } = useAutoSave({
    debounceMs: 2000,
    enabled: !!presentationData && !isStreaming,
  });

  // Custom hooks
  const { fetchUserSlides } = usePresentationData(
    presentation_id,
    setLoading,
    setError
  );

  const { fetchFinalPresentationData } = useFinalPresentationData(
    presentation_id,
    setLoading,
    setError
  );

  const {
    isPresentMode,
    stream,
    handleSlideClick,
    toggleFullscreen,
    handlePresentExit,
    handleSlideChange,
  } = usePresentationNavigation(
    presentation_id,
    selectedSlide,
    setSelectedSlide,
    setIsFullscreen
  );

  // Debug: Log current state
  console.log('🔍 PresentationPage - Current state:', {
    hasPresentationData: !!presentationData,
    slidesCount: presentationData?.slides?.length || 0,
    loading,
    isStreaming,
    stream,
    hasOutlines: !!outlines,
    outlinesLength: outlines?.length || 0
  });

  // Debug: Log slide data
  if (presentationData?.slides) {
    console.log('🔍 PresentationPage - Slide data:', presentationData.slides.map((slide: any, index: number) => ({
      index,
      id: slide.id,
      layout: slide.layout,
      layout_group: slide.layout_group,
      content: slide.content,
      contentType: typeof slide.content
    })));
  }

  // Add timeout to prevent infinite loading
  useEffect(() => {
    if (stream && isStreaming) {
      const timeout = setTimeout(() => {
        console.warn('⚠️ Streaming timeout - forcing completion');
        // Force completion if streaming takes too long
        if (presentationData?.slides && presentationData.slides.length > 0) {
          // If we have slides, assume streaming is complete
          window.location.href = `/presentation?id=${presentation_id}`;
        }
      }, 60000); // 60 second timeout

      return () => clearTimeout(timeout);
    }
  }, [stream, isStreaming, presentationData, presentation_id]);

  // Initialize streaming only if presentation is prepared
  usePresentationStreaming(
    presentation_id,
    stream,
    setLoading,
    setError,
    fetchUserSlides
  );

  usePresentationUndoRedo();

  const onSlideChange = (newSlide: number) => {
    handleSlideChange(newSlide, presentationData);
  };


  // Check presentation status immediately on mount
  useEffect(() => {
    const checkPresentationStatus = async () => {
      try {
        // First try to load from final presentations (new approach)
        await fetchFinalPresentationData();
      } catch (error) {
        console.error('Error checking presentation status:', error);
        // Don't set loading to false immediately, let the streaming logic handle it
        console.log('🔍 Final presentation data fetch failed, will try regular presentation data');
      }
    };

    checkPresentationStatus();
  }, [presentation_id, fetchFinalPresentationData]);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    let readinessCheckTimeout: NodeJS.Timeout;
    
    // Check if presentation is not prepared (missing layout/outlines)
    // Only run this check after we've had a chance to load data
    // Don't run readiness check if we're in streaming mode
    if (!loading && !isStreaming && !stream && presentationData !== null) {
      // Add a small delay to ensure all data is loaded
      readinessCheckTimeout = setTimeout(() => {
      console.log('🔍 Presentation readiness check:', {
        loading,
        isStreaming,
        stream,
        hasLayout: !!presentationData?.layout,
        hasOutlines: !!outlines && outlines.length > 0,
        hasSlides: !!presentationData?.slides && presentationData?.slides.length > 0,
        layout: presentationData?.layout,
        outlines: outlines,
        outlinesType: typeof outlines,
        outlinesLength: outlines?.length,
        slides: presentationData?.slides
      });
      
      // If we have slides, the presentation is ready regardless of layout/outlines
      const hasSlides = presentationData?.slides && presentationData?.slides.length > 0;
      const hasLayout = !!presentationData?.layout;
      const hasOutlines = !!outlines && outlines.length > 0;
      
      // Only show error if we don't have slides AND we're missing required preparation data
      if (!hasSlides && (!hasLayout || !hasOutlines)) {
        console.log('🔍 Presentation not prepared (missing layout/outlines and no slides), showing error state');
        console.log('🔍 Detailed check:', {
          hasPresentationData: !!presentationData,
          hasLayout,
          hasOutlines,
          hasSlides,
          outlinesLength: outlines?.length,
          slidesLength: presentationData?.slides?.length,
          presentationDataKeys: presentationData ? Object.keys(presentationData) : null
        });
        // Add a small delay to prevent showing error too early
        timeoutId = setTimeout(() => {
          setError(true);
        }, 1000);
      } else if (hasSlides) {
        console.log('✅ Presentation has slides, clearing any error state');
        setError(false);
      }
      
      // If layout and outlines exist but no slides, and we're not streaming, try to trigger streaming
      if (hasLayout && hasOutlines && !hasSlides) {
        console.log('🔍 Presentation prepared but no slides, may need streaming');
        // Don't set error here, let streaming handle it
      }
      }, 500); // 500ms delay to ensure data is loaded
    }
    
    // If we're in streaming mode, clear any error state and show loading
    if (stream) {
      console.log('🔄 Streaming mode detected, clearing error state and showing loading');
      setError(false);
    }
    
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      if (readinessCheckTimeout) {
        clearTimeout(readinessCheckTimeout);
      }
    };

    if(!loading && !isStreaming && presentationData?.slides && presentationData?.slides.length > 0){  
      const presentation_id = presentationData?.slides[0].layout.split(":")[0].split("custom-")[1];
    const fonts = getCustomTemplateFonts(presentation_id);
  
    useFontLoader(fonts || []);
  }
  }, [presentationData, loading, isStreaming, outlines, stream]);
  // Presentation Mode View
  if (isPresentMode) {
    return (
      <PresentationMode
        slides={presentationData?.slides || []}
        currentSlide={selectedSlide}
        isFullscreen={isFullscreen}
        onFullscreenToggle={toggleFullscreen}
        onExit={handlePresentExit}
        onSlideChange={onSlideChange}
      />
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
        <div
          className="bg-white border border-orange-300 text-orange-700 px-6 py-8 rounded-lg shadow-lg flex flex-col items-center max-w-md mx-auto"
          role="alert"
        >
          <AlertCircle className="w-16 h-16 mb-4 text-orange-500" />
          <h2 className="text-xl font-semibold mb-2">Presentation Not Ready</h2>
          <p className="text-center mb-4 text-sm">
            This presentation needs to be prepared first. Please complete the outline generation and template selection process.
          </p>
          <div className="flex flex-col gap-3 w-full">
            <Button 
              onClick={() => { 
                trackEvent(MixpanelEvent.Navigation, { pathname, action: 'go_to_outline' }); 
                window.location.href = '/outline'; 
              }}
              className="w-full"
            >
              Go to Outline Page
            </Button>
            <Button 
              variant="outline"
              onClick={() => { 
                trackEvent(MixpanelEvent.PresentationPage_Refresh_Page_Button_Clicked, { pathname }); 
                window.location.reload(); 
              }}
              className="w-full"
            >
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex overflow-hidden flex-col">
      <SavingIndicator isSaving={isAutoSaving} isSaved={isSaved} />
      
      <Header presentation_id={presentation_id} currentSlide={selectedSlide} />
      <Help />

      <div
        style={{
          background: "#1a1a1a",
        }}
        className="flex flex-1 relative"
      >
        <SidePanel
          selectedSlide={selectedSlide}
          onSlideClick={handleSlideClick}
          loading={loading}
          isMobilePanelOpen={isMobilePanelOpen}
          setIsMobilePanelOpen={setIsMobilePanelOpen}
        />
        
        <div className="flex-1 h-[calc(100vh-100px)] overflow-y-auto bg-[#1a1a1a]">
          <div
            id="presentation-slides-wrapper"
            className="mx-auto flex flex-col items-center overflow-hidden justify-center p-4"
          >
            {error ? (
              <div className="relative w-full h-[calc(100vh-120px)] mx-auto flex items-center justify-center">
                <div className="text-center">
                  <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Presentation Not Ready</h2>
                  <p className="text-gray-600 mb-4">
                    This presentation needs to be prepared first. Please go back to the outline page to prepare it.
                  </p>
                  <Button 
                    onClick={() => window.location.href = '/outline'}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Go to Outline Page
                  </Button>
                </div>
              </div>
            ) : !presentationData ||
            loading ||
            isStreaming ||
            (stream && isStreaming) || // Only show loading if stream=true AND actually streaming
            !presentationData?.slides ||
            presentationData?.slides.length === 0 ? (
              <div className="relative w-full h-[calc(100vh-120px)] mx-auto">
                <div className="">
                  {Array.from({ length: 2 }).map((_, index) => (
                    <Skeleton
                      key={index}
                      className="aspect-video bg-[#404040] my-4 w-full mx-auto max-w-[1280px]"
                    />
                  ))}
                </div>
                {(loading || isStreaming) && (
                  <div className="relative">
                    <LoadingState 
                      message={
                        isStreaming
                          ? "Generating slides with AI..." 
                          : loading 
                          ? "Loading your presentation..." 
                          : undefined
                      } 
                    />
                    {/* Add skip button if streaming takes too long */}
                    {stream && (
                      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
                        <Button
                          variant="outline"
                          onClick={() => {
                            console.log('🔍 User clicked skip loading');
                            window.location.href = `/presentation?id=${presentation_id}`;
                          }}
                          className="bg-white/90 hover:bg-white text-gray-800 border-gray-300"
                        >
                          Skip Loading
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => {
                            console.log('🔍 User clicked force complete');
                            // Force complete by removing stream parameter and reloading
                            const url = new URL(window.location.href);
                            url.searchParams.delete('stream');
                            window.location.href = url.toString();
                          }}
                          className="bg-blue-500/90 hover:bg-blue-500 text-white border-blue-500"
                        >
                          Force Complete
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <>
                {presentationData &&
                  presentationData.slides &&
                  presentationData.slides.length > 0 &&
                  presentationData.slides.map((slide: any, index: number) => (
                    <SlideContent
                      key={`${slide.type}-${index}-${slide.index}`}
                      slide={slide}
                      index={index}
                      presentationId={presentation_id}
                    />
                  ))}
              </>
            )}
          </div>
        </div>

        {/* Right Sidebar - PowerPoint-style editing tools */}
        <div className="w-[60px] bg-[#2d2d2d] border-l border-[#404040] flex flex-col items-center py-4">
          {/* Search */}
          <div className="mb-4">
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>

          {/* Text */}
          <div className="mb-4">
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <span className="text-sm font-bold">Aa</span>
            </button>
          </div>

          {/* Image */}
          <div className="mb-4">
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </button>
          </div>

          {/* Grid/Layout */}
          <div className="mb-4">
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </button>
          </div>

          {/* NEW Badge */}
          <div className="mb-4 relative">
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </button>
            <div className="absolute -top-1 -right-1 bg-[#0078d4] text-white text-xs px-1 rounded text-[10px] font-bold">
              NEW
            </div>
          </div>

          {/* Chart */}
          <div className="mb-4">
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </button>
          </div>

          {/* Video */}
          <div className="mb-4">
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
          </div>

          {/* Table */}
          <div className="mb-4">
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0V4a1 1 0 011-1h16a1 1 0 011 1v16a1 1 0 01-1 1H4a1 1 0 01-1-1z" />
              </svg>
            </button>
          </div>

          {/* Line */}
          <div className="mb-4">
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>

          {/* Pen/Edit */}
          <div className="mb-4">
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
            </button>
          </div>

          {/* Spacer */}
          <div className="flex-1"></div>

          {/* Zoom level */}
          <div className="mb-2">
            <span className="text-[#a0a0a0] text-xs">100%</span>
          </div>

          {/* Help */}
          <div>
            <button className="w-10 h-10 bg-[#404040] hover:bg-[#505050] rounded flex items-center justify-center text-white">
              <span className="text-sm font-bold">?</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PresentationPage;

