import { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { toast } from "sonner";
import { setOutlines } from "@/store/slices/presentationGeneration";
import { jsonrepair } from "jsonrepair";
import { RootState } from "@/store/store";



export const useOutlineStreaming = (presentationId: string | null, onStreamingComplete?: () => void) => {
  const dispatch = useDispatch();
  const { outlines } = useSelector((state: RootState) => state.presentationGeneration);
  const [isStreaming, setIsStreaming] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [activeSlideIndex, setActiveSlideIndex] = useState<number | null>(null);
  const [highestActiveIndex, setHighestActiveIndex] = useState<number>(-1);
  const prevSlidesRef = useRef<{ content: string }[]>([]);
  const activeIndexRef = useRef<number>(-1);
  const highestIndexRef = useRef<number>(-1);

  useEffect(() => {
    if (!presentationId || outlines.length > 0) return;

    let eventSource: EventSource;
    let accumulatedChunks = "";

    const initializeStream = async () => {
      setIsStreaming(true)
      setIsLoading(true)
      try {
        // Get token from localStorage for EventSource authentication
        const token = localStorage.getItem('authToken');
        console.log('🔍 useOutlineStreaming: Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'None');
        
        const url = token 
          ? `/api/v1/ppt/outlines/stream/${presentationId}?token=${encodeURIComponent(token)}`
          : `/api/v1/ppt/outlines/stream/${presentationId}`;
        
        console.log('🔍 useOutlineStreaming: EventSource URL:', url);
        eventSource = new EventSource(url);

        eventSource.addEventListener("response", (event) => {
          const data = JSON.parse(event.data);
          switch (data.type) {
            case "chunk":
              // 
              accumulatedChunks += data.chunk;
              // 
              try {
                const repairedJson = jsonrepair(accumulatedChunks);
                const partialData = JSON.parse(repairedJson);

                if (partialData && Array.isArray(partialData.slides)) {
                  // ✅ Structured JSON format from Gemini
                  const nextSlides: { content: string }[] = partialData.slides || [];
                  // Determine which slide index changed to minimize live parsing
                  try {
                    const prev = prevSlidesRef.current || [];
                    let changedIndex: number | null = null;
                    const maxLen = Math.max(prev.length, nextSlides.length);
                    for (let i = 0; i < maxLen; i++) {
                      const prevContent = prev[i]?.content;
                      const nextContent = nextSlides[i]?.content;
                      if (nextContent !== prevContent) {
                        changedIndex = i;
                      }
                    }
                    // Keep active index stable if no change detected; and ensure non-decreasing
                    const prevActive = activeIndexRef.current;
                    let nextActive = changedIndex ?? prevActive;
                    if (nextActive < prevActive) {
                      nextActive = prevActive;
                    }
                    activeIndexRef.current = nextActive;
                    setActiveSlideIndex(nextActive);

                    if (nextActive > highestIndexRef.current) {
                      highestIndexRef.current = nextActive;
                      setHighestActiveIndex(nextActive);
                    }
                  } catch { }

                  prevSlidesRef.current = nextSlides;
                  dispatch(setOutlines(nextSlides));
                  setIsLoading(false)
                } else if (partialData && typeof partialData.outline === "string") {
                  // ✅ Plain text fallback — wrap into slide format
                  console.log("🧠 Frontend: Received plain text outline, wrapping into slide format");
                  const outlineSlides = [
                    {
                      content: partialData.outline
                    }
                  ];
                  prevSlidesRef.current = outlineSlides;
                  dispatch(setOutlines(outlineSlides));
                  setIsLoading(false);
                } else {
                  console.warn("⚠️ Unknown data format received:", partialData);
                }
              } catch (error) {
                // JSON isn't complete yet, continue accumulating
                console.log("🔄 JSON parsing in progress, continuing to accumulate chunks");
              }
              break;

            case "complete":
              try {
                console.log("🧠 Frontend: Processing complete event", data);
                
                // Handle different response formats safely
                let outlinesData: { content: string }[] = [];
                
                if (data?.presentation?.outlines?.slides && Array.isArray(data.presentation.outlines.slides)) {
                  // ✅ Standard structured response
              
                  console.log("✅ Using structured slides from presentation.outlines.slides");
                } else if (data?.presentation?.outlines && typeof data.presentation.outlines === "string") {
                  // ✅ Plain text outline in presentation.outlines
                  console.log("🧠 Frontend: Received plain text outline in presentation.outlines, wrapping into slide format");
                  outlinesData = [
                    {
                      content: data.presentation.outlines
                    }
                  ];
                } else if (accumulatedChunks) {
                  // ✅ Try to parse accumulated chunks as fallback
                  try {
                    const repairedJson = jsonrepair(accumulatedChunks);
                    const parsedData = JSON.parse(repairedJson);
                    
                    if (parsedData && Array.isArray(parsedData.slides)) {
                      outlinesData = parsedData.slides.map((slide: any) => ({
                        content: slide.content || slide.slideContent || slide
                      }));
                      console.log("✅ Using slides from accumulated chunks");
                    } else if (parsedData && typeof parsedData.outline === "string") {
                      console.log("🧠 Frontend: Received plain text outline in accumulated chunks, wrapping into slide format");
                      outlinesData = [
                        {
                          content: parsedData.outline
                        }
                      ];
                    } else {
                      console.warn("⚠️ Unknown format in accumulated chunks:", parsedData);
                      outlinesData = [
                        {
                          content: accumulatedChunks || "No outline content received"
                        }
                      ];
                    }
                  } catch (parseError) {
                    console.warn("⚠️ Failed to parse accumulated chunks, using as plain text");
                    outlinesData = [
                      {
                        content: accumulatedChunks || "No outline content received"
                      }
                    ];
                  }
                } else {
                  console.warn("⚠️ No outline data found in complete event");
                  outlinesData = [
                    {
                      content: "No outline content received"
                    }
                  ];
                }
                
                dispatch(setOutlines(outlinesData));
                setIsStreaming(false)
                setIsLoading(false)
                setActiveSlideIndex(null)
                setHighestActiveIndex(-1)
                prevSlidesRef.current = outlinesData;
                activeIndexRef.current = -1;
                highestIndexRef.current = -1;
                eventSource.close();
                
                // Trigger callback when streaming completes
                if (onStreamingComplete) {
                  onStreamingComplete();
                }
              } catch (error) {
                console.error("❌ Error parsing complete event:", error, data);
                toast.error("Failed to parse presentation data");
                eventSource.close();
              }
              accumulatedChunks = "";
              break;

            case "closing":

              setIsStreaming(false)
              setIsLoading(false)
              setActiveSlideIndex(null)
              setHighestActiveIndex(-1)
              activeIndexRef.current = -1;
              highestIndexRef.current = -1;
              eventSource.close();
              
              // Trigger callback when streaming closes
              if (onStreamingComplete) {
                onStreamingComplete();
              }
              break;
            case "error":

              setIsStreaming(false)
              setIsLoading(false)
              setActiveSlideIndex(null)
              setHighestActiveIndex(-1)
              activeIndexRef.current = -1;
              highestIndexRef.current = -1;
              eventSource.close();
              toast.error('Error in outline streaming',
                {
                  description: data.detail || 'Failed to connect to the server. Please try again.',
                }
              );
              // Don't trigger callback on error - let user handle manually
              break;
          }
        });

        eventSource.onerror = () => {

          setIsStreaming(false)
          setIsLoading(false)
          setActiveSlideIndex(null)
          setHighestActiveIndex(-1)
          activeIndexRef.current = -1;
          highestIndexRef.current = -1;
          eventSource.close();
          toast.error("Failed to connect to the server. Please try again.");
          // Don't trigger callback on error - let user handle manually
        };
      } catch (error) {

        setIsStreaming(false)
        setIsLoading(false)
        setActiveSlideIndex(null)
        setHighestActiveIndex(-1)
        activeIndexRef.current = -1;
        highestIndexRef.current = -1;
        toast.error("Failed to initialize connection");
        // Don't trigger callback on error - let user handle manually
      }
    };
    initializeStream();
    return () => {
      if (eventSource) {
        eventSource.close();
      }
    };
  }, [presentationId, dispatch]);

  return { isStreaming, isLoading, activeSlideIndex, highestActiveIndex };
}; 