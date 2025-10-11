"use client";
import React, { useState, useEffect } from "react";
import { LayoutList, ListTree, PanelRightOpen, X } from "lucide-react";
import ToolTip from "@/components/ToolTip";
import { Button } from "@/components/ui/button";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "@/store/store";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { setPresentationData } from "@/store/slices/presentationGeneration";
import { SortableSlide } from "./SortableSlide";
import { SortableListItem } from "./SortableListItem";
import { useTemplateLayouts } from "../../hooks/useTemplateLayouts";

interface SidePanelProps {
  selectedSlide: number;
  onSlideClick: (index: number) => void;
  isMobilePanelOpen: boolean;
  setIsMobilePanelOpen: (value: boolean) => void;
  loading: boolean;
}

const SidePanel = ({
  selectedSlide,
  onSlideClick,
  isMobilePanelOpen,
  setIsMobilePanelOpen,
  loading,
}: SidePanelProps) => {
  const [isOpen, setIsOpen] = useState(true);
  const [active, setActive] = useState<"list" | "grid">("grid");

  const { presentationData, isStreaming } = useSelector(
    (state: RootState) => state.presentationGeneration
  );

  const dispatch = useDispatch();

  // Use the centralized group layouts hook
  const { renderSlideContent } = useTemplateLayouts();

  useEffect(() => {
    if (window.innerWidth < 768) {
      setIsOpen(isMobilePanelOpen);
    }
  }, [isMobilePanelOpen]);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Start drag after moving 8px
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleClose = () => {
    setIsOpen(false);
    if (window.innerWidth < 768) {
      setIsMobilePanelOpen(false);
    }
  };

  const handleDragEnd = (event: any) => {
    const { active, over } = event;

    if (!active || !over || !presentationData?.slides) return;

    // Filter out null/undefined slides before processing
    const validSlides = presentationData.slides.filter((slide: any) => slide && slide.id);
    
    if (active.id !== over.id) {
      // Find the indices of the dragged and target items
      const oldIndex = validSlides.findIndex(
        (item: any) => item.id === active.id
      );
      const newIndex = validSlides.findIndex(
        (item: any) => item.id === over.id
      );

      if (oldIndex === -1 || newIndex === -1) return;

      // Reorder the array
      const reorderedArray = arrayMove(
        validSlides,
        oldIndex,
        newIndex
      );

      // Update indices of all slides
      const updatedArray = reorderedArray.map((slide: any, index: number) => ({
        ...slide,
        index: index,
      }));

      // Update the store with new order and indices
      dispatch(
        setPresentationData({ ...presentationData, slides: updatedArray })
      );
    }
  };

  // Loading shimmer component
  if (
    !presentationData ||
    loading ||
    !presentationData?.slides ||
    presentationData?.slides.length === 0
  ) {
    return null;
  }

  // Debug: Log slide data to identify null/undefined slides
  console.log('🔍 SidePanel - Presentation data:', presentationData);
  console.log('🔍 SidePanel - Slides:', presentationData?.slides);
  console.log('🔍 SidePanel - Slide IDs:', presentationData?.slides?.map((slide: any, index: number) => ({
    index,
    id: slide?.id,
    hasId: !!slide?.id,
    slide: slide
  })));

  return (
    <>
      {/* Desktop Toggle Button - Always visible when panel is closed */}
      {!isOpen && (
        <div className="hidden xl:block fixed left-4 top-1/2 -translate-y-1/2 z-50">
          <ToolTip content="Open Panel">
            <Button
              onClick={() => setIsOpen(true)}
              className="bg-white hover:bg-gray-50 shadow-lg"
            >
              <PanelRightOpen className="text-black" size={20} />
            </Button>
          </ToolTip>
        </div>
      )}

      {/* Mobile Toggle Button */}
      {!isMobilePanelOpen && (
        <div className="xl:hidden fixed left-4 bottom-4 z-50">
          <ToolTip content="Show Panel">
            <Button
              onClick={() => setIsMobilePanelOpen(true)}
              className="bg-[#5146E5] text-white p-3 rounded-full shadow-lg"
            >
              <PanelRightOpen className="text-white" size={20} />
            </Button>
          </ToolTip>
        </div>
      )}

      <div
        className={`
          fixed xl:relative h-full z-50 xl:z-auto
          transition-all duration-300 ease-in-out
          ${isOpen ? "ml-0" : "-ml-[300px]"}
          ${isMobilePanelOpen
            ? "translate-x-0"
            : "-translate-x-full xl:translate-x-0"
          }
        `}
      >
        <div className="w-[280px] bg-[#2d2d2d] h-[calc(100vh-100px)] flex flex-col border-r border-[#404040]">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-[#404040]">
            <div className="flex items-center gap-2">
              <Button
                className="bg-[#404040] hover:bg-[#505050] text-white border-0"
                onClick={() => {
                  if (!isStreaming) {
                    setActive("grid")
                  }
                }}
              >
                <LayoutList size={16} />
              </Button>
              <Button
                className="bg-[#404040] hover:bg-[#505050] text-white border-0"
                onClick={() => {
                  if (!isStreaming) {
                    setActive("list")
                  }
                }}
              >
                <ListTree size={16} />
              </Button>
            </div>
            <X
              onClick={handleClose}
              className="text-[#a0a0a0] cursor-pointer hover:text-white"
              size={18}
            />
          </div>

          {/* New Slide Button */}
          <div className="p-4 border-b border-[#404040]">
            <Button className="w-full bg-[#0078d4] hover:bg-[#106ebe] text-white border-0">
              + New
            </Button>
          </div>

          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            {/* PowerPoint-style Slide List */}
            <div className="flex-1 overflow-y-auto">
              {isStreaming ? (
                presentationData &&
                presentationData?.slides
                  ?.filter((slide: any) => slide && slide.id) // Filter out null/undefined slides
                  ?.map((slide: any, index: number) => (
                    <div
                      key={`${index}-${slide.type}-${slide.id}`}
                      className={`flex items-center gap-3 p-3 cursor-pointer hover:bg-[#404040] border-l-4 ${
                        selectedSlide === index ? 'border-[#0078d4] bg-[#404040]' : 'border-transparent'
                      }`}
                      onClick={() => onSlideClick(index)}
                    >
                      <div className="w-8 h-8 bg-[#404040] rounded flex items-center justify-center text-white text-sm font-medium">
                        {index + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-white text-sm font-medium truncate">
                          {slide.content?.title || `Slide ${index + 1}`}
                        </div>
                      </div>
                    </div>
                  ))
              ) : (
                <SortableContext
                  items={
                    presentationData?.slides
                      ?.filter((slide: any) => slide && slide.id) // Filter out null/undefined slides
                      ?.map((slide: any) => slide.id) || []
                  }
                  strategy={verticalListSortingStrategy}
                >
                  <div id={`slide-${selectedSlide}`}>
                    {presentationData &&
                      presentationData?.slides
                        ?.filter((slide: any) => slide && slide.id) // Filter out null/undefined slides
                        ?.map((slide: any, index: number) => (
                          <div
                            key={`${slide.id}-${index}`}
                            className={`flex items-center gap-3 p-3 cursor-pointer hover:bg-[#404040] border-l-4 ${
                              selectedSlide === index ? 'border-[#0078d4] bg-[#404040]' : 'border-transparent'
                            }`}
                            onClick={() => onSlideClick(index)}
                          >
                            <div className="w-8 h-8 bg-[#404040] rounded flex items-center justify-center text-white text-sm font-medium">
                              {index + 1}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="text-white text-sm font-medium truncate">
                                {slide.content?.title || `Slide ${index + 1}`}
                              </div>
                            </div>
                          </div>
                        ))}
                  </div>
                </SortableContext>
              )}
            </div>

          </DndContext>
        </div>
      </div>
    </>
  );
};

export default SidePanel;
