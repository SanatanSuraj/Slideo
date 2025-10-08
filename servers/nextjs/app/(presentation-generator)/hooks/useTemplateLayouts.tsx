"use client";
import React, { useMemo } from "react";
import { useDispatch } from "react-redux";
import { useLayout } from "../context/LayoutContext";
import EditableLayoutWrapper from "../components/EditableLayoutWrapper";
import SlideErrorBoundary from "../components/SlideErrorBoundary";
import TiptapTextReplacer from "../components/TiptapTextReplacer";
import { updateSlideContent } from "../../../store/slices/presentationGeneration";
import { Loader2 } from "lucide-react";

export const useTemplateLayouts = () => {
  const dispatch = useDispatch();
  const { getLayoutById, getLayout, loading } =
    useLayout();

  const getTemplateLayout = useMemo(() => {
    return (layoutId: string, groupName: string) => {
      const layout = getLayoutById(layoutId);
      if (layout) {
        return getLayout(layoutId);
      }
      return null;
    };
  }, [getLayoutById, getLayout]);



  // Render slide content with group validation, automatic Tiptap text editing, and editable images/icons
  const renderSlideContent = useMemo(() => {
    return (slide: any, isEditMode: boolean) => {
      // Safety check for required slide properties
      if (!slide || !slide.layout || !slide.layout_group) {
        return (
          <div className="flex flex-col items-center justify-center aspect-video h-full bg-gray-100 rounded-lg">
            <p className="text-gray-600 text-center text-base">
              Slide data incomplete. Missing layout information.
            </p>
          </div>
        );
      }

      const Layout = getTemplateLayout(slide.layout, slide.layout_group);
      if (loading) {
        return (
          <div className="flex flex-col items-center justify-center aspect-video h-full bg-gray-100 rounded-lg">
            <Loader2 className="w-8 h-8 animate-spin text-blue-800" />
          </div>
        );
      }
      if (!Layout) {
        return (
          <div className="flex flex-col items-center justify-center aspect-video h-full bg-gray-100 rounded-lg">
            <p className="text-gray-600 text-center text-base">
              Layout &quot;{slide.layout}&quot; not found in &quot;
              {slide.layout_group}&quot; group
            </p>
          </div>
        );
      }

      if (isEditMode) {
        return (
          <EditableLayoutWrapper
            slideIndex={slide.index}
            slideData={slide.content}
            properties={slide.properties}
          >
            <TiptapTextReplacer
              key={slide.id}
              slideData={slide.content}
              slideIndex={slide.index}
              onContentChange={(
                content: string,
                dataPath: string,
                slideIndex?: number
              ) => {
                if (dataPath && slideIndex !== undefined) {
                  dispatch(
                    updateSlideContent({
                      slideIndex: slideIndex,
                      dataPath: dataPath,
                      content: content,
                    })
                  );
                }
              }}
            >
              <SlideErrorBoundary label={`Slide ${slide.index + 1}`}>
                <Layout data={slide.content} />
              </SlideErrorBoundary>
            </TiptapTextReplacer>
          </EditableLayoutWrapper>
        );
      }
      // Debug: Log the slide content to see what's being passed to the template
      console.log(`🔍 Slide ${slide.index + 1} content:`, slide.content);
      console.log(`🔍 Slide ${slide.index + 1} content type:`, typeof slide.content);
      console.log(`🔍 Slide ${slide.index + 1} content keys:`, Object.keys(slide.content || {}));
      
      // Debug: Check for author/date fields specifically
      if (slide.content) {
        console.log(`🔍 Slide ${slide.index + 1} - Looking for author/date fields:`);
        console.log(`🔍 - introCard:`, slide.content.introCard);
        console.log(`🔍 - presenterName:`, slide.content.presenterName);
        console.log(`🔍 - presentationDate:`, slide.content.presentationDate);
        console.log(`🔍 - All nested keys:`, JSON.stringify(slide.content, null, 2));
      }
      
      return (
        <SlideErrorBoundary label={`Slide ${slide.index + 1}`}>
          <Layout data={slide.content} />
        </SlideErrorBoundary>
      );
    };
  }, [getTemplateLayout, dispatch]);

  return {
    getTemplateLayout,
    renderSlideContent,
    loading,
  };
};
