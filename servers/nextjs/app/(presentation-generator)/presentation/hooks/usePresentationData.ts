import { useCallback } from "react";
import { useDispatch } from "react-redux";
import { toast } from "sonner";
import { setPresentationData, setOutlines } from "@/store/slices/presentationGeneration";
import { DashboardApi } from '../../services/api/dashboard';
import {  clearHistory } from "@/store/slices/undoRedoSlice";


export const usePresentationData = (
  presentationId: string,
  setLoading: (loading: boolean) => void,
  setError: (error: boolean) => void
) => {
  const dispatch = useDispatch();

  const fetchUserSlides = useCallback(async () => {
    try {
      // First, try to get the final edit version if it exists
      const token = localStorage.getItem('authToken');
      if (token) {
        try {
          const finalEditResponse = await fetch(`/api/v1/presentation_final_edits/get/${presentationId}`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (finalEditResponse.ok) {
            const finalEditData = await finalEditResponse.json();
            console.log('✅ Loading presentation from final edit data');
            
            // Convert final edit data to presentation format
            const processedData = {
              id: finalEditData.presentation_id,
              title: finalEditData.title,
              language: 'en', // Default language
              layout: {
                name: 'Final Edit Layout',
                ordered: true,
                slides: []
              },
              n_slides: finalEditData.slides?.total_slides || 0,
              slides: finalEditData.slides?.slides?.map((slide: any, index: number) => {
                if (slide.content && typeof slide.content === 'string') {
                  try {
                    const parsedContent = JSON.parse(slide.content);
                    return {
                      ...slide,
                      id: slide.id || `slide-${index}`, // Ensure slide has an ID
                      content: parsedContent
                    };
                  } catch (error) {
                    console.warn('Failed to parse slide content:', error);
                    return {
                      ...slide,
                      id: slide.id || `slide-${index}` // Ensure slide has an ID
                    };
                  }
                }
                return {
                  ...slide,
                  id: slide.id || `slide-${index}` // Ensure slide has an ID
                };
              }) || []
            };
            
            dispatch(setPresentationData(processedData));
            dispatch(clearHistory());
            setLoading(false);
            return;
          }
        } catch (error) {
          console.log('⚠️ No final edit found, falling back to regular presentation data');
        }
      }

      // Fallback to regular presentation data
      const response = await DashboardApi.getPresentation(presentationId);
      if (response) {
        // Extract presentation data from the response
        const data = response.data || response;
        console.log('🔍 Presentation data from API:', data);
        
        // Check if presentation is properly prepared
        if (!data.structure || !data.outlines) {
          console.log('🔍 Presentation not prepared, setting error state');
          console.log('🔍 Structure:', data.structure);
          console.log('🔍 Outlines:', data.outlines);
          setError(true);
          setLoading(false);
          toast.error("Presentation not ready", {
            description: "This presentation needs to be prepared first. Please complete the outline generation and template selection process.",
            action: {
              label: "Go to Outline",
              onClick: () => window.location.href = '/outline'
            }
          });
          return;
        }
        
        // Parse slide content from JSON string to object
        const processedData = {
          ...data,
          slides: data.slides?.map((slide: any) => {
            if (slide.content && typeof slide.content === 'string') {
              try {
                const parsedContent = JSON.parse(slide.content);
                return {
                  ...slide,
                  content: parsedContent
                };
              } catch (error) {
                console.warn('Failed to parse slide content:', error);
                return slide;
              }
            }
            return slide;
          }) || []
        };
        
        dispatch(setPresentationData(processedData));
        
        // Dispatch outlines if they exist
        console.log('🔍 Outlines data structure:', {
          hasOutlines: !!data.outlines,
          hasSlides: !!data.outlines?.slides,
          isArray: Array.isArray(data.outlines?.slides),
          slidesLength: data.outlines?.slides?.length,
          slidesData: data.outlines?.slides
        });
        
        if (data.outlines && data.outlines.slides && Array.isArray(data.outlines.slides)) {
          console.log('🔍 Dispatching outlines to Redux store:', data.outlines.slides);
          dispatch(setOutlines(data.outlines.slides));
        } else {
          console.log('🔍 Outlines not in expected format, skipping dispatch');
        }
        
        dispatch(clearHistory());
        setLoading(false);
      }
    } catch (error) {
      setError(true);
      toast.error("Failed to load presentation");
      console.error("Error fetching user slides:", error);
      setLoading(false);
    }
  }, [presentationId, dispatch, setLoading, setError]);

  return {
    fetchUserSlides,
  };
};
