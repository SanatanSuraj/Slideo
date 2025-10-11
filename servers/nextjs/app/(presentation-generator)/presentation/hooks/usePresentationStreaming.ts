import { useEffect, useRef } from "react";
import { useDispatch } from "react-redux";
import { useRouter, useSearchParams } from "next/navigation";
import {
  clearPresentationData,
  setPresentationData,
  setStreaming,
  setSaving,
  setSaved,
  setOutlines,
} from "@/store/slices/presentationGeneration";
import { jsonrepair } from "jsonrepair";
import { toast } from "sonner";
import { MixpanelEvent, trackEvent } from "@/utils/mixpanel";
import { StreamingClient, StreamingEvent } from "@/utils/streamingClient";

export const usePresentationStreaming = (
  presentationId: string,
  stream: string | null,
  setLoading: (loading: boolean) => void,
  setError: (error: boolean) => void,
  fetchUserSlides: () => void
) => {
  const dispatch = useDispatch();
  const router = useRouter();
  const searchParams = useSearchParams();
  const previousSlidesLength = useRef(0);
  const streamingClientRef = useRef<StreamingClient | null>(null);

  const startStreaming = (token: string) => {
    console.log('🔍 Starting presentation streaming with custom client...');
    console.log('🔍 Presentation ID:', presentationId);
    console.log('🔍 Token:', token ? `${token.substring(0, 20)}...` : 'None');
    
    if (!presentationId) {
      console.error('❌ No presentation ID provided for streaming');
      setError(true);
      setLoading(false);
      dispatch(setStreaming(false));
      return;
    }
    
    // Close any existing connection
    if (streamingClientRef.current) {
      streamingClientRef.current.disconnect();
      streamingClientRef.current = null;
    }
    
    const url = `/api/v1/ppt/presentation/stream/${presentationId}`;
    console.log('🔍 Streaming URL:', url);
    
    let accumulatedChunks = "";
    
    streamingClientRef.current = new StreamingClient(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      timeout: 60000,
      
      onOpen: () => {
        console.log('✅ Streaming connection opened successfully');
      },
      
      onMessage: (event: StreamingEvent) => {
        try {
          console.log('🔍 Stream event received:', event);
          
          if (event.event === 'response') {
            const data = JSON.parse(event.data);
            console.log('🔍 Stream data parsed:', data);
            
            if (data.type === "chunk") {
              accumulatedChunks += data.chunk;
              
              try {
                // Try to parse the accumulated chunks as JSON
                const repairedJson = jsonrepair(accumulatedChunks);
                const parsedData = JSON.parse(repairedJson);
                
                if (parsedData.slides && Array.isArray(parsedData.slides)) {
                  console.log('🔍 Setting presentation data with slides:', parsedData.slides.length);
                  console.log('🔍 First slide content:', parsedData.slides[0]?.content);
                  console.log('🔍 First slide content type:', typeof parsedData.slides[0]?.content);
                  
                  // Parse slide content from JSON string to object
                  const processedSlides = parsedData.slides.map((slide: any) => {
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
                  });
                  
                  const processedData = {
                    ...parsedData,
                    slides: processedSlides
                  };
                  
                  dispatch(setPresentationData(processedData));
                }
              } catch (parseError) {
                // Not complete JSON yet, continue accumulating
                console.log('🔍 Accumulating chunks, not complete JSON yet');
              }
            } else if (data.type === "complete") {
              console.log('🔍 Stream completed with final data:', data);
              if (data.presentation) {
                // Parse slide content from JSON string to object for complete data
                const processedPresentation = {
                  ...data.presentation,
                  slides: data.presentation.slides?.map((slide: any) => {
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
                dispatch(setPresentationData(processedPresentation));
              }
              setLoading(false);
              dispatch(setStreaming(false));
              
              // Clear the streaming timeout
              clearTimeout(streamingTimeout);
              
              // Show saving indicator
              dispatch(setSaving(true));
              
              // Update URL to remove stream parameter and show success message
              const currentParams = new URLSearchParams(searchParams.toString());
              if (currentParams.has('stream')) {
                currentParams.delete('stream');
                // Remove existing id parameter to avoid duplication
                currentParams.delete('id');
                // Add the presentation ID back
                currentParams.set('id', presentationId);
                const newUrl = `/presentation?${currentParams.toString()}`;
                router.replace(newUrl, { scroll: false });
                
                // Simulate saving process and show success
                setTimeout(() => {
                  dispatch(setSaving(false));
                  dispatch(setSaved(true));
                  
                  // Show success message
                  toast.success("✅ Saved to Cloud", {
                    description: "Your presentation has been automatically saved and is ready to use.",
                    duration: 3000,
                  });
                  
                  // Hide saved indicator after 3 seconds
                  setTimeout(() => {
                    dispatch(setSaved(false));
                  }, 3000);
                }, 1000); // 1 second delay to show saving indicator
              }
            }
          }
        } catch (error) {
          console.error('❌ Error parsing stream data:', error);
        }
      },
      
      onError: (error: Error) => {
        console.error('❌ Streaming error:', error);
        
        // Check if it's a preparation error
        if (error.message.includes('not prepared') || error.message.includes('outlines are missing')) {
          console.log('🔍 Preparation error detected, showing error state');
          setError(true);
          setLoading(false);
          dispatch(setStreaming(false));
          toast.error("Presentation not ready", {
            description: "This presentation needs to be prepared first. Please complete the outline generation and template selection process.",
            action: {
              label: "Go to Outline",
              onClick: () => window.location.href = '/outline'
            }
          });
          return;
        }
        
        console.log('🔍 Falling back to direct fetch...');
        
        // Fallback to direct fetch for other errors
        fetchUserSlides();
        setLoading(false);
        dispatch(setStreaming(false));
        
        toast.error("Streaming failed", {
          description: "Falling back to direct loading. Your presentation should still load.",
        });
      },
      
      onClose: () => {
        console.log('🔍 Streaming connection closed');
        setLoading(false);
        dispatch(setStreaming(false));
      }
    });
    
    // Start the connection
    streamingClientRef.current.connect().catch((error) => {
      console.error('❌ Failed to start streaming:', error);
      setError(true);
      setLoading(false);
      dispatch(setStreaming(false));
      
      // Clear the streaming timeout
      clearTimeout(streamingTimeout);
    });
  };

  useEffect(() => {
    const initializeStream = async () => {
      // Early exit if no presentation ID
      if (!presentationId) {
        return;
      }
      dispatch(setStreaming(true));
      dispatch(clearPresentationData());

      // Add timeout to prevent infinite streaming
      const streamingTimeout = setTimeout(() => {
        console.warn('⚠️ Streaming timeout - forcing completion');
        setLoading(false);
        dispatch(setStreaming(false));
      }, 120000); // 2 minute timeout

      trackEvent(MixpanelEvent.Presentation_Stream_API_Call);

      // Get authentication headers using the proper auth system
      const { getAuthHeader } = await import('../../services/api/header');
      const authHeaders = getAuthHeader();
      console.log('🔍 usePresentationStreaming: Auth headers:', authHeaders);
      
      // If no auth token, skip the API call and let other hooks handle it
      if (!authHeaders.Authorization) {
        console.log('🔍 No auth token available, skipping streaming initialization');
        setLoading(false);
        dispatch(setStreaming(false));
        setError(false);
        return;
      }
      
      // COMPLETELY DIFFERENT APPROACH: Check if presentation is prepared first
      try {
        const checkResponse = await fetch(`/api/v1/ppt/presentation/${presentationId}`, {
          method: 'GET',
          headers: {
            ...authHeaders,
            'Content-Type': 'application/json',
          },
        });

        if (!checkResponse.ok) {
          throw new Error('Failed to fetch presentation');
        }

        const response = await checkResponse.json();
        console.log('🔍 Presentation response:', response);

        // Extract presentation data from the response
        const presentation = response.data || response;
        console.log('🔍 Presentation data:', presentation);

        // Check if presentation has required fields
        // If we have slides, the presentation is ready regardless of structure/outlines
        const hasSlides = presentation.slides && presentation.slides.length > 0;
        const hasStructure = presentation.structure;
        const hasOutlines = presentation.outlines;
        
        if (!hasSlides && (!hasStructure || !hasOutlines)) {
          console.log('❌ Presentation not prepared, showing error state');
          console.log('🔍 Structure:', presentation.structure);
          console.log('🔍 Outlines:', presentation.outlines);
          console.log('🔍 Slides:', presentation.slides);
          setLoading(false);
          dispatch(setStreaming(false));
          setError(true);
          
          // Only show error toast if not in streaming mode
          if (!stream) {
            toast.error("Presentation not ready", {
              description: "This presentation needs to be prepared first. Please complete the outline generation and template selection process.",
              action: {
                label: "Go to Outline",
                onClick: () => window.location.href = '/outline'
              }
            });
          }
          return;
        }
        
        // If we have slides, the presentation is ready - no need to stream
        if (hasSlides) {
          console.log('✅ Presentation has slides, loading existing slides');
          setLoading(false);
          dispatch(setStreaming(false));
          setError(false);
          
          // Parse slide content from JSON string to object
          const processedData = {
            ...presentation,
            slides: presentation.slides?.map((slide: any) => {
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
          if (presentation.outlines && presentation.outlines.slides && Array.isArray(presentation.outlines.slides)) {
            dispatch(setOutlines(presentation.outlines.slides));
          }
          
          return;
        }

        // If presentation is prepared, check if we should stream or just fetch slides
        if (stream) {
          // Check if presentation is already saved as final edit
          try {
            const checkResponse = await fetch(`/api/v1/presentation_final_edits/check/${presentationId}`, {
              method: 'GET',
              headers: {
                ...authHeaders,
                'Content-Type': 'application/json',
              },
            });

            if (checkResponse.ok) {
              const isAlreadySaved = await checkResponse.json();
              if (isAlreadySaved) {
                console.log('✅ Presentation already saved as final edit, loading from DB...');
                fetchUserSlides();
                setLoading(false);
                dispatch(setStreaming(false));
                return;
              }
            }
          } catch (error) {
            console.warn('⚠️ Failed to check if presentation is saved, proceeding with streaming:', error);
          }

          console.log('✅ Presentation is prepared and stream requested, starting streaming...');
          // Start actual streaming to generate slides
          const token = authHeaders.Authorization?.replace('Bearer ', '') || '';
          startStreaming(token);
        } else {
          console.log('✅ Presentation is prepared, fetching slides...');
          fetchUserSlides();
          setLoading(false);
          dispatch(setStreaming(false));
        }

      } catch (error) {
        console.error('❌ Error checking presentation:', error);
        setLoading(false);
        dispatch(setStreaming(false));
        
        // Check if it's an authentication error
        if (error instanceof Error && (error.message.includes('credentials') || error.message.includes('token'))) {
          console.log('🔍 Authentication error detected, falling back to regular data loading');
          setError(false);
          // Don't show error toast for auth issues, let other hooks handle it
          return;
        }
        
        setError(true);
        toast.error("Failed to load presentation", {
          description: "There was an error loading the presentation. Please try again or go back to the outline page.",
          action: {
            label: "Go to Outline",
            onClick: () => window.location.href = '/outline'
          }
        });
      }
    };

    // ALWAYS check presentation status first, regardless of stream parameter
    if (presentationId) {
      initializeStream();
    }

    return () => {
      // Cleanup StreamingClient if it exists
      if (streamingClientRef.current) {
        streamingClientRef.current.disconnect();
        streamingClientRef.current = null;
      }
    };
  }, [presentationId, stream, dispatch, setLoading, setError, fetchUserSlides]);
};
