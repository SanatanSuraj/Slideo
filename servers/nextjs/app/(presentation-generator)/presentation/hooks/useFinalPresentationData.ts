import { useCallback } from "react";
import { useDispatch } from "react-redux";
import { toast } from "sonner";
import { setPresentationData, setOutlines } from "@/store/slices/presentationGeneration";
import { clearHistory } from "@/store/slices/undoRedoSlice";

export const useFinalPresentationData = (
  presentationId: string,
  setLoading: (loading: boolean) => void,
  setError: (error: boolean) => void
) => {
  const dispatch = useDispatch();

  const fetchFinalPresentationData = useCallback(async () => {
    try {
      console.log(`🔍 Attempting to load final presentation data for: ${presentationId}`);
      
      // First, try to get the final presentation from the new collection
      try {
        const finalPresentationResponse = await fetch(`/api/v1/final_presentations/test/by-presentation/${presentationId}`);
        
        if (finalPresentationResponse.ok) {
          const finalPresentationData = await finalPresentationResponse.json();
          
          if (finalPresentationData.found) {
            console.log('✅ Loading presentation from final_presentations collection');
            
            const data = finalPresentationData.data;
            
            // Convert final presentation data to presentation format
            const processedData = {
              id: data.presentation_id,
              title: data.title,
              language: data.language || 'en',
              layout: data.layout || {
                name: 'Final Presentation Layout',
                ordered: true,
                slides: []
              },
              structure: data.structure || {},
              outlines: data.outlines || {},
              n_slides: data.total_slides || 0,
              slides: data.slides?.slides?.map((slide: any, index: number) => {
                if (slide.content && typeof slide.content === 'string') {
                  try {
                    const parsedContent = JSON.parse(slide.content);
                    return {
                      ...slide,
                      id: slide.id || `slide-${index}`,
                      content: parsedContent
                    };
                  } catch (error) {
                    console.warn('Failed to parse slide content:', error);
                    return {
                      ...slide,
                      id: slide.id || `slide-${index}`
                    };
                  }
                }
                return {
                  ...slide,
                  id: slide.id || `slide-${index}`
                };
              }) || []
            };
            
            dispatch(setPresentationData(processedData));
            dispatch(clearHistory());
            setLoading(false);
            return;
          }
        }
      } catch (error) {
        console.log('⚠️ No final presentation found in final_presentations collection, trying presentation_final_edits');
      }
      
      // Fallback to presentation_final_edits collection
      try {
        const finalEditResponse = await fetch(`/api/v1/presentation_final_edits/test/${presentationId}`);
        
        if (finalEditResponse.ok) {
          const finalEditData = await finalEditResponse.json();
          
          if (finalEditData.found) {
            console.log('✅ Loading presentation from presentation_final_edits collection');
            
            const data = finalEditData.data;
            
            // Fetch the original presentation to get layout, structure, and outlines
            let layout = null;
            let structure = null;
            let outlines = null;
            
            try {
              const token = localStorage.getItem('authToken');
              const originalPresentationResponse = await fetch(`/api/v1/ppt/presentation/${presentationId}`, {
                method: 'GET',
                headers: token ? { 'Authorization': `Bearer ${token}` } : {},
              });
              
              if (originalPresentationResponse.ok) {
                const originalData = await originalPresentationResponse.json();
                layout = originalData.layout;
                structure = originalData.structure;
                outlines = originalData.outlines;
                console.log('✅ Loaded layout, structure, and outlines from original presentation');
              }
            } catch (error) {
              console.warn('Failed to fetch original presentation for layout/structure/outlines:', error);
            }
            
            // Convert final edit data to presentation format
            const processedData = {
              id: data.presentation_id,
              title: data.title,
              language: 'en',
              layout: layout || {
                name: 'Final Edit Layout',
                ordered: true,
                slides: []
              },
              structure: structure || {},
              outlines: outlines || {},
              n_slides: data.slides?.total_slides || 0,
              slides: data.slides?.slides?.map((slide: any, index: number) => {
                if (slide.content && typeof slide.content === 'string') {
                  try {
                    const parsedContent = JSON.parse(slide.content);
                    return {
                      ...slide,
                      id: slide.id || `slide-${index}`,
                      content: parsedContent
                    };
                  } catch (error) {
                    console.warn('Failed to parse slide content:', error);
                    return {
                      ...slide,
                      id: slide.id || `slide-${index}`
                    };
                  }
                }
                return {
                  ...slide,
                  id: slide.id || `slide-${index}`
                };
              }) || []
            };
            
            dispatch(setPresentationData(processedData));
            
            // Dispatch outlines if they exist
            console.log('🔍 Final presentation outlines data structure:', {
              hasOutlines: !!data.outlines,
              hasSlides: !!data.outlines?.slides,
              isArray: Array.isArray(data.outlines?.slides),
              slidesLength: data.outlines?.slides?.length,
              slidesData: data.outlines?.slides
            });
            
            if (data.outlines && data.outlines.slides && Array.isArray(data.outlines.slides)) {
              console.log('🔍 Final presentation: Dispatching outlines to Redux store:', data.outlines.slides);
              dispatch(setOutlines(data.outlines.slides));
            } else {
              console.log('🔍 Final presentation: Outlines not in expected format, skipping dispatch');
            }
            
            dispatch(clearHistory());
            setLoading(false);
            setError(false);
            return;
          }
        }
      } catch (error) {
        console.log('⚠️ No final edit found in presentation_final_edits collection');
      }
      
      // If no final presentation or final edit found, show error
      console.log('❌ No final presentation data found, showing error state');
      setError(true);
      setLoading(false);
      toast.error("Presentation not ready", {
        description: "This presentation needs to be prepared first. Please complete the outline generation and template selection process.",
        action: {
          label: "Go to Outline",
          onClick: () => window.location.href = '/outline'
        }
      });
      
    } catch (error) {
      console.error("Error fetching final presentation data:", error);
      setError(true);
      setLoading(false);
      toast.error("Failed to load presentation");
    }
  }, [presentationId, dispatch, setLoading, setError]);

  return {
    fetchFinalPresentationData,
  };
};
