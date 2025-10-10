"use client";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "@/store/store";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { usePathname } from "next/navigation";
import { trackEvent, MixpanelEvent } from "@/utils/mixpanel";
import { AlertCircle } from "lucide-react";
import { setPresentationData } from "@/store/slices/presentationGeneration";
import { DashboardApi } from "../services/api/dashboard";
import { useLayout } from "../context/LayoutContext";
import { useFontLoader } from "../hooks/useFontLoader";
import { useTemplateLayouts } from "../hooks/useTemplateLayouts";





const PresentationPage = ({ presentation_id, authToken }: { presentation_id: string, authToken?: string | null }) => {
  const { renderSlideContent, loading: templateLoading } = useTemplateLayouts();
  const pathname = usePathname();
  const [contentLoading, setContentLoading] = useState(true);
  const { getCustomTemplateFonts, loading: layoutLoading } = useLayout()
  const dispatch = useDispatch();
  const { presentationData } = useSelector(
    (state: RootState) => state.presentationGeneration
  );
  const [error, setError] = useState(false);
  useEffect(() => {
    if (!templateLoading && !layoutLoading && presentationData?.slides && presentationData?.slides.length > 0) {
      const presentation_id = presentationData?.slides[0].layout.split(":")[0].split("custom-")[1];
      const fonts = getCustomTemplateFonts(presentation_id);

      useFontLoader(fonts || []);
    }
  }, [presentationData, templateLoading, layoutLoading]);
  useEffect(() => {
    if (presentationData?.slides[0].layout.includes("custom")) {
      const existingScript = document.querySelector(
        'script[src*="tailwindcss.com"]'
      );
      if (!existingScript) {
        const script = document.createElement("script");
        script.src = "https://cdn.tailwindcss.com";
        script.async = true;
        document.head.appendChild(script);
      }
    }
  }, [presentationData]);
  // Function to fetch the slides
  useEffect(() => {
    fetchUserSlides();
  }, []);

  // Function to fetch the user slides
  const fetchUserSlides = async () => {
    try {
      // If authToken is provided, set it in localStorage first
      if (authToken) {
        localStorage.setItem('authToken', authToken);
        console.log('🔧 PDF Maker: Token set in localStorage from URL parameter');
      }
      
      console.log('🔧 PDF Maker: Fetching presentation data...');
      const data = await DashboardApi.getPresentation(presentation_id);
      console.log('🔧 PDF Maker: Presentation data received:', {
        hasSlides: !!data?.slides,
        slideCount: data?.slides?.length,
        firstSlide: data?.slides?.[0] ? {
          layout: data.slides[0].layout,
          layout_group: data.slides[0].layout_group,
          hasContent: !!data.slides[0].content
        } : null
      });

      // Process the slides data to ensure proper formatting for template rendering
      const processedData = {
        ...data,
        slides: data.slides?.map((slide: any, index: number) => {
          // Parse slide content from JSON string to object if needed
          let parsedContent = slide.content;
          if (slide.content && typeof slide.content === 'string') {
            try {
              parsedContent = JSON.parse(slide.content);
            } catch (error) {
              console.warn('Failed to parse slide content:', error);
              parsedContent = slide.content;
            }
          }

          // Ensure the slide has the proper structure for template rendering
          return {
            ...slide,
            id: slide.id || `slide-${index}`,
            index: index,
            content: parsedContent,
            // Ensure speaker_note exists for export
            speaker_note: slide.notes || slide.speaker_note || '',
            // Ensure layout properties are properly set
            layout: slide.layout || 'default',
            layout_group: slide.layout_group || 'default',
            // Add properties if missing
            properties: slide.properties || {}
          };
        }) || []
      };

      console.log('🔧 PDF Maker: Processed slides data:', {
        slideCount: processedData.slides.length,
        firstSlideContent: processedData.slides[0]?.content,
        firstSlideLayout: processedData.slides[0]?.layout
      });

      dispatch(setPresentationData(processedData));
      setContentLoading(false);
    } catch (error) {
      setError(true);
      toast.error("Failed to load presentation");
      console.error("Error fetching user slides:", error);
      setContentLoading(false);
    }
  };

  // Regular view
  return (
    <div className="flex overflow-hidden flex-col">
      {error ? (
        <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
          <div
            className="bg-white border border-red-300 text-red-700 px-6 py-8 rounded-lg shadow-lg flex flex-col items-center"
            role="alert"
          >
            <AlertCircle className="w-16 h-16 mb-4 text-red-500" />
            <strong className="font-bold text-4xl mb-2">Oops!</strong>
            <p className="block text-2xl py-2">
              We encountered an issue loading your presentation.
            </p>
            <p className="text-lg py-2">
              Please check your internet connection or try again later.
            </p>
            <Button
              className="mt-4 bg-red-500 text-white hover:bg-red-600 focus:ring-4 focus:ring-red-300"
              onClick={() => {
                trackEvent(MixpanelEvent.PdfMaker_Retry_Button_Clicked, { pathname });
                window.location.reload();
              }}
            >
              Retry
            </Button>
          </div>
        </div>
      ) : (
        <div className="">
          <div
            id="presentation-slides-wrapper"
            className="mx-auto flex flex-col items-center  overflow-hidden  justify-center   "
          >
            {!presentationData ||
              templateLoading ||
              layoutLoading ||
              contentLoading ||
              !presentationData?.slides ||
              presentationData?.slides.length === 0 ? (
              <div className="relative w-full h-[calc(100vh-120px)] mx-auto ">
                <div className=" ">
                  {Array.from({ length: 2 }).map((_, index) => (
                    <Skeleton
                      key={index}
                      className="aspect-video bg-gray-400 my-4 w-full mx-auto max-w-[1280px]"
                    />
                  ))}
                </div>
              </div>
            ) : (
              <>
                {presentationData &&
                  presentationData.slides &&
                  presentationData.slides.length > 0 &&
                  presentationData.slides.map((slide: any, index: number) => {
                    console.log('🔧 PDF Maker: Rendering slide', index, {
                      layout: slide.layout,
                      layout_group: slide.layout_group,
                      hasContent: !!slide.content,
                      contentType: typeof slide.content,
                      contentKeys: slide.content ? Object.keys(slide.content) : [],
                      templateLoading,
                      layoutLoading
                    });
                    
                    // Additional validation for slide content
                    if (!slide.content || (typeof slide.content === 'object' && Object.keys(slide.content).length === 0)) {
                      console.warn(`🔧 PDF Maker: Slide ${index} has empty or missing content:`, slide.content);
                    }
                    
                    return (
                      // [data-speaker-note] is used to extract the speaker note from the slide for export to pptx
                      <div key={index} className="w-full" data-speaker-note={slide.speaker_note}>
                        {renderSlideContent(slide, false)}
                      </div>
                    );
                  })}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default PresentationPage;
