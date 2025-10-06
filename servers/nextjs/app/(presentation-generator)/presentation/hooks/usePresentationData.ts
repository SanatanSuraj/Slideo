import { useCallback } from "react";
import { useDispatch } from "react-redux";
import { toast } from "sonner";
import { setPresentationData } from "@/store/slices/presentationGeneration";
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
      const data = await DashboardApi.getPresentation(presentationId);
      if (data) {
        // Check if presentation is properly prepared
        if (!data.structure || !data.outlines) {
          console.log('🔍 Presentation not prepared, setting error state');
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
        
        dispatch(setPresentationData(data));
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
