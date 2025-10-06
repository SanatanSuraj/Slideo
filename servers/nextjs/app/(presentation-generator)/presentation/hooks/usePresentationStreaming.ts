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

export const usePresentationStreaming = (
  presentationId: string,
  stream: string | null,
  setLoading: (loading: boolean) => void,
  setError: (error: boolean) => void,
  fetchUserSlides: () => void
) => {
  const dispatch = useDispatch();
  const previousSlidesLength = useRef(0);

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
            description: "This presentation needs to be prepared first. Please go back to the outline page to prepare it.",
          });
          return;
        }

        // If presentation is prepared, check if we should stream or just fetch slides
        if (stream) {
          console.log('✅ Presentation is prepared and stream requested, starting streaming...');
          // Start actual streaming here if needed
          // For now, just fetch slides normally
          fetchUserSlides();
        } else {
          console.log('✅ Presentation is prepared, fetching slides...');
          fetchUserSlides();
        }
        setLoading(false);
        dispatch(setStreaming(false));

      } catch (error) {
        console.error('❌ Error checking presentation:', error);
        setLoading(false);
        dispatch(setStreaming(false));
        setError(true);
        toast.error("Failed to load presentation", {
          description: "There was an error loading the presentation. Please try again or go back to the outline page.",
        });
      }
    };

    // ALWAYS check presentation status first, regardless of stream parameter
    initializeStream();

    return () => {
      // No cleanup needed for this approach
    };
  }, [presentationId, stream, dispatch, setLoading, setError, fetchUserSlides]);
};
