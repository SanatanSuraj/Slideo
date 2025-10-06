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
  usePresentationNavigation,
  useAutoSave,
} from "../hooks";
import { PresentationPageProps } from "../types";
import LoadingState from "./LoadingState";
import { useLayout } from "../../context/LayoutContext";
import { useFontLoader } from "../../hooks/useFontLoader";
import { usePresentationUndoRedo } from "../hooks/PresentationUndoRedo";
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
 
  const { presentationData, isStreaming } = useSelector(
    (state: RootState) => state.presentationGeneration
  );

  // Auto-save functionality
  const { isSaving } = useAutoSave({
    debounceMs: 2000,
    enabled: !!presentationData && !isStreaming,
  });

  // Custom hooks
  const { fetchUserSlides } = usePresentationData(
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
        const token = localStorage.getItem('authToken');
        const response = await fetch(`/api/v1/ppt/presentation/${presentation_id}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const presentation = await response.json();
          if (!presentation.structure || !presentation.outlines) {
            console.log('🔍 Presentation not prepared, showing error state');
            setLoading(false);
            setError(true);
            toast.error("Presentation not ready", {
              description: "This presentation needs to be prepared first. Please go back to the outline page.",
            });
            return;
          }
        }
      } catch (error) {
        console.error('Error checking presentation status:', error);
        setLoading(false);
      }
    };

    checkPresentationStatus();
  }, [presentation_id]);

  useEffect(() => {
    // Check if presentation is not prepared (missing structure/outlines)
    if (!loading && !isStreaming && !presentationData?.slides && !presentationData?.structure && !presentationData?.outlines) {
      console.log('🔍 Presentation not prepared, showing error state');
      setError(true);
      return;
    }

    if(!loading && !isStreaming && presentationData?.slides && presentationData?.slides.length > 0){  
      const presentation_id = presentationData?.slides[0].layout.split(":")[0].split("custom-")[1];
    const fonts = getCustomTemplateFonts(presentation_id);
  
    useFontLoader(fonts || []);
  }
  }, [presentationData,loading,isStreaming]);
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
          className="bg-white border border-red-300 text-red-700 px-6 py-8 rounded-lg shadow-lg flex flex-col items-center"
          role="alert"
        >
          <AlertCircle className="w-16 h-16 mb-4 text-red-500" />
          <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
          <p className="text-center mb-4">
            We couldn't load your presentation. This might be because the presentation hasn't been prepared yet.
          </p>
          <div className="flex gap-3">
            <Button 
              variant="outline"
              onClick={() => { 
                trackEvent(MixpanelEvent.PresentationPage_Go_To_Outline_Button_Clicked, { pathname }); 
                window.location.href = '/outline'; 
              }}
            >
              Go to Outline
            </Button>
            <Button onClick={() => { 
              trackEvent(MixpanelEvent.PresentationPage_Refresh_Page_Button_Clicked, { pathname }); 
              window.location.reload(); 
            }}>
              Refresh Page
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex overflow-hidden flex-col">
      <div className="fixed right-6 top-[5.2rem] z-50">
        {isSaving && <Loader2 className="w-6 h-6 animate-spin text-blue-500" />}
      </div>

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
                {stream && <LoadingState />}
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
