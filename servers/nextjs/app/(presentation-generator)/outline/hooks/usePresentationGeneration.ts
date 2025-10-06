import { useState, useCallback } from "react";
import { useDispatch } from "react-redux";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { clearPresentationData } from "@/store/slices/presentationGeneration";
import { PresentationGenerationApi } from "../../services/api/presentation-generation";
import { Template, LoadingState, TABS } from "../types/index";
import { MixpanelEvent, trackEvent } from "@/utils/mixpanel";

const DEFAULT_LOADING_STATE: LoadingState = {
  message: "",
  isLoading: false,
  showProgress: false,
  duration: 0,
};

export const usePresentationGeneration = (
  presentationId: string | null,
  outlines: { content: string }[] | null,
  selectedTemplate: Template | null,
  setActiveTab: (tab: string) => void
) => {
  const dispatch = useDispatch();
  const router = useRouter();
  const [loadingState, setLoadingState] = useState<LoadingState>(DEFAULT_LOADING_STATE);

  const validateInputs = useCallback(() => {
    if (!outlines || outlines.length === 0) {
      toast.error("No Outlines", {
        description: "Please wait for outlines to load before generating presentation",
      });
      return false;
    }

    if (!selectedTemplate) {
      toast.error("Select Layout Group", {
        description: "Please select a layout group before generating presentation",
      });
      return false;
    }
    if (!selectedTemplate.slides || !selectedTemplate.slides.length) {
      toast.error("No Slide Schema found", {
        description: "Please select a Group before generating presentation",
      });
      return false;
    }

    return true;
  }, [outlines, selectedTemplate]);

  const prepareLayoutData = useCallback(() => {
    if (!selectedTemplate || !selectedTemplate.slides) return null;
    return {
      name: selectedTemplate.name,
      ordered: selectedTemplate.ordered,
      slides: selectedTemplate.slides
    };
  }, [selectedTemplate]);

  const handleSubmit = useCallback(async () => {
    if (!selectedTemplate) {
      setActiveTab(TABS.LAYOUTS);
      return;
    }
    if (!validateInputs()) return;



    setLoadingState({
      message: "Generating presentation data...",
      isLoading: true,
      showProgress: true,
      duration: 30,
    });

    try {
      const layoutData = prepareLayoutData();

      if (!layoutData) {
        console.error('No layout data available');
        toast.error("Layout Error", {
          description: "No layout data available. Please select a template.",
        });
        return;
      }
      
      trackEvent(MixpanelEvent.Presentation_Prepare_API_Call);
      console.log('Preparing presentation with data:', {
        presentation_id: presentationId,
        outlines: outlines?.length,
        layout: layoutData
      });
      
      const response = await PresentationGenerationApi.presentationPrepare({
        presentation_id: presentationId,
        outlines: outlines,
        layout: layoutData,
      });

      console.log('Presentation preparation response:', response);
      
      if (response) {
        dispatch(clearPresentationData());
        // Redirect to presentation page to show the prepared presentation
        router.replace(`/presentation?id=${presentationId}&stream=true`);
      } else {
        console.error('No response from presentation preparation');
        toast.error("Preparation Error", {
          description: "Failed to prepare presentation. Please try again.",
        });
      }
    } catch (error: any) {
      console.error('Error In Presentation Generation(prepare).', error);
      toast.error("Generation Error", {
        description: error.message || "Error In Presentation Generation(prepare).",
      });
    } finally {
      setLoadingState(DEFAULT_LOADING_STATE);
    }
  }, [validateInputs, prepareLayoutData, presentationId, outlines, dispatch, router, selectedTemplate]);

  return { loadingState, handleSubmit };
}; 