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
    if (!loading && !isStreaming && presentationData !== null) {
      // Add a small delay to ensure all data is loaded
      readinessCheckTimeout = setTimeout(() => {
      console.log('🔍 Presentation readiness check:', {
        loading,
        isStreaming,
        hasLayout: !!presentationData?.layout,
        hasOutlines: !!outlines && outlines.length > 0,
        hasSlides: !!presentationData?.slides && presentationData?.slides.length > 0,
        layout: presentationData?.layout,
        outlines: outlines,
        outlinesType: typeof outlines,
        outlinesLength: outlines?.length,
        slides: presentationData?.slides
      });
      
      // If no layout or outlines, presentation is not prepared
      // But if we have slides, the presentation is ready regardless of outlines
      const hasSlides = presentationData?.slides && presentationData?.slides.length > 0;
      const hasLayout = !!presentationData?.layout;
      const hasOutlines = !!outlines && outlines.length > 0;
      
      if (!hasLayout || (!hasOutlines && !hasSlides)) {
        console.log('🔍 Presentation not prepared (missing layout/outlines), showing error state');
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
      }
      
      // If layout and outlines exist but no slides, and we're not streaming, try to trigger streaming
      if (hasLayout && hasOutlines && !hasSlides) {
        console.log('🔍 Presentation prepared but no slides, may need streaming');
        // Don't set error here, let streaming handle it
      }
      }, 500); // 500ms delay to ensure data is loaded
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
  }, [presentationData, loading, isStreaming, outlines]);
  // Presentation Mode View
  if (isPresentMode) {
    return (
      <PresentationMode
        slides={presentationData?.slides!}
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
          background: "#c8c7c9",
        }}
        className="flex flex-1 relative pt-6"
      >
        <SidePanel
          selectedSlide={selectedSlide}
          onSlideClick={handleSlideClick}
          loading={loading}
          isMobilePanelOpen={isMobilePanelOpen}
          setIsMobilePanelOpen={setIsMobilePanelOpen}
        />
        
        <div className="flex-1 h-[calc(100vh-100px)] overflow-y-auto">
          <div
            id="presentation-slides-wrapper"
            className="mx-auto flex flex-col items-center overflow-hidden justify-center p-2 sm:p-6 pt-0"
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
            !presentationData?.slides ||
            presentationData?.slides.length === 0 ? (
              <div className="relative w-full h-[calc(100vh-120px)] mx-auto">
                <div className="">
                  {Array.from({ length: 2 }).map((_, index) => (
                    <Skeleton
                      key={index}
                      className="aspect-video bg-gray-400 my-4 w-full mx-auto max-w-[1280px]"
                    />
                  ))}
                </div>
                {(stream || loading) && (
                  <LoadingState 
                    message={
                      loading && !stream 
                        ? "Loading your presentation..." 
                        : stream 
                        ? "Generating slides with AI..." 
                        : undefined
                    } 
                  />
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
      </div>
    </div>
  );
};

export default PresentationPage;

