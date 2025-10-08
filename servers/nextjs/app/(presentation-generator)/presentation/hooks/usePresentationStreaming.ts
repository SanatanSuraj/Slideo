import { useEffect, useRef } from "react";
import { useDispatch } from "react-redux";
import {
  clearPresentationData,
  setPresentationData,
  setStreaming,
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
              console.log('🔍 Stream completed with final data');
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
    });
  };

  useEffect(() => {
    // Early exit if no presentation ID
    if (!presentationId) {
      return;
    }

    const initializeStream = async () => {
      dispatch(setStreaming(true));
      dispatch(clearPresentationData());

      trackEvent(MixpanelEvent.Presentation_Stream_API_Call);

      // Get token from localStorage for authentication
      const token = localStorage.getItem('authToken');
      console.log('🔍 usePresentationStreaming: Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'None');
      
      // COMPLETELY DIFFERENT APPROACH: Check if presentation is prepared first
      try {
        const checkResponse = await fetch(`/api/v1/ppt/presentation/${presentationId}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!checkResponse.ok) {
          throw new Error('Failed to fetch presentation');
        }

        const presentation = await checkResponse.json();
        console.log('🔍 Presentation data:', presentation);

        // Check if presentation has required fields
        if (!presentation.structure || !presentation.outlines) {
          console.log('❌ Presentation not prepared, showing error state');
          setLoading(false);
          dispatch(setStreaming(false));
          setError(true);
          toast.error("Presentation not ready", {
            description: "This presentation needs to be prepared first. Please complete the outline generation and template selection process.",
            action: {
              label: "Go to Outline",
              onClick: () => window.location.href = '/outline'
            }
          });
          return;
        }

        // If presentation is prepared, check if we should stream or just fetch slides
        if (stream) {
          console.log('✅ Presentation is prepared and stream requested, starting streaming...');
          // Start actual streaming to generate slides
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
    initializeStream();

    return () => {
      // Cleanup StreamingClient if it exists
      if (streamingClientRef.current) {
        streamingClientRef.current.disconnect();
        streamingClientRef.current = null;
      }
    };
  }, [presentationId, stream, dispatch, setLoading, setError, fetchUserSlides]);
};
