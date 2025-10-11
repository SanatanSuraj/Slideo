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
  const { getLayoutById, getLayout, loading, getAllLayouts } =
    useLayout();

  const getTemplateLayout = useMemo(() => {
    const buildLayoutCandidates = (rawLayoutId?: string, rawGroupName?: string) => {
      const layoutId = rawLayoutId?.trim() ?? "";
      const initialGroup = rawGroupName?.trim();

      const candidateKeys = new Set<string>();
      const candidateGroups = new Set<string>();
      let baseLayoutId = layoutId;

      if (initialGroup) {
        candidateGroups.add(initialGroup);
      }

      if (layoutId.includes(":")) {
        const parts = layoutId.split(":").filter(Boolean);
        if (parts.length >= 2) {
          const extractedGroup = parts.shift()!;
          const remainder = parts.join(":");
          baseLayoutId = remainder || extractedGroup;

          candidateGroups.add(extractedGroup);
          candidateKeys.add(`${extractedGroup}:${remainder}`);

          if (initialGroup && initialGroup !== extractedGroup) {
            candidateKeys.add(`${initialGroup}:${remainder}`);
          }
        }
      }

      if (layoutId) {
        candidateKeys.add(layoutId);
      }

      if (initialGroup && layoutId && !layoutId.includes(":")) {
        candidateKeys.add(`${initialGroup}:${layoutId}`);
      }

      if (!baseLayoutId) {
        baseLayoutId = layoutId;
      }

      return {
        baseLayoutId,
        candidateKeys: Array.from(candidateKeys).filter(Boolean),
        candidateGroups: Array.from(candidateGroups).filter(Boolean),
      };
    };

    return (layoutId: string, groupName?: string) => {
      const { baseLayoutId, candidateKeys, candidateGroups } = buildLayoutCandidates(
        layoutId,
        groupName
      );

      const fallbackGroupSet = new Set<string>([
        ...(candidateGroups || []),
        ...(groupName ? [groupName] : []),
        "standard",
      ]);

      console.log(`🔍 getTemplateLayout - Looking for layout:`, {
        layoutId,
        groupName,
        candidateKeys,
        baseLayoutId,
        fallbackGroups: Array.from(fallbackGroupSet),
        loading,
      });

      // Debug: Log all available layouts
      const allLayouts = getAllLayouts();
      console.log(
        `🔍 getTemplateLayout - All available layouts:`,
        allLayouts.map((l) => l.id)
      );

      let resolvedKey: string | null = null;
      for (const key of candidateKeys) {
        const layoutInfo = getLayoutById(key);
        if (layoutInfo) {
          resolvedKey = key;
          break;
        }
      }

      if (resolvedKey) {
        const LayoutComponent = getLayout(resolvedKey);
        console.log(`🔍 getTemplateLayout - Resolved layout component:`, {
          resolvedKey,
          LayoutComponent,
        });
        return LayoutComponent;
      }

      // Fallback: Try to find a similar layout in the same group
      console.warn(
        `⚠️ getTemplateLayout - Layout not found for candidates ${candidateKeys.join(
          ", "
        )}, trying fallbacks...`
      );

      const layoutMappings: { [key: string]: string } = {
        "split-left-strip-header-title-subtitle-cards-slide":
          "heading-bullet-image-description-layout",
        "split-left-strip-header-title-subtitle-cards":
          "heading-bullet-image-description-layout",
        "cards-slide": "heading-bullet-image-description-layout",
        "title-subtitle-cards": "heading-bullet-image-description-layout",
        "split-left-strip": "heading-bullet-image-description-layout",
        "header-counter-two-column-image-text-slide":
          "heading-bullet-image-description-layout",
        "intro-slide": "intro-slide-layout",
        "intro-slide-layout": "intro-slide-layout",
        "contact-slide": "contact-layout",
        "contact-layout": "contact-layout",
        "table-of-contents": "table-of-contents-layout",
        "table-of-contents-layout": "table-of-contents-layout",
      };

      const mappedLayoutId =
        layoutMappings[baseLayoutId] ?? layoutMappings[layoutId];
      if (mappedLayoutId) {
        for (const fallbackGroup of fallbackGroupSet) {
          const mappedKey = `${fallbackGroup}:${mappedLayoutId}`;
          const mappedLayout = getLayoutById(mappedKey);
          if (mappedLayout) {
            console.log(
              `✅ getTemplateLayout - Using mapped layout: ${mappedKey}`
            );
            return getLayout(mappedKey);
          }
        }
      }

      const fallbackLayoutIds = [
        "heading-bullet-image-description-layout", // HeadingBulletImageDescriptionLayout
        "icon-image-description-layout", // IconImageDescriptionLayout
        "intro-slide-layout", // IntroSlideLayout
        "table-of-contents-layout", // TableOfContentsLayout
        "contact-layout", // ContactLayout
      ];

      for (const fallbackGroup of fallbackGroupSet) {
        for (const layoutOption of fallbackLayoutIds) {
          const fallbackKey = `${fallbackGroup}:${layoutOption}`;
          const fallbackLayout = getLayoutById(fallbackKey);
          if (fallbackLayout) {
            console.log(
              `✅ getTemplateLayout - Using fallback layout: ${fallbackKey}`
            );
            return getLayout(fallbackKey);
          }
        }
      }

      console.error(
        `❌ getTemplateLayout - No fallback layout found for layoutId=${layoutId}, groupName=${groupName}`
      );
      return null;
    };
  }, [getAllLayouts, getLayout, getLayoutById, loading]);



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

      let Layout = getTemplateLayout(slide.layout, slide.layout_group);
      
      // Debug: Log layout resolution
      console.log(`🔍 Slide ${slide.index + 1} - Layout resolution:`, {
        requestedLayout: slide.layout,
        requestedGroup: slide.layout_group,
        resolvedLayout: Layout,
        layoutType: typeof Layout
      });
      if (loading) {
        return (
          <div className="flex flex-col items-center justify-center aspect-video h-full bg-gray-100 rounded-lg">
            <Loader2 className="w-8 h-8 animate-spin text-blue-800" />
          </div>
        );
      }
      if (!Layout) {
        console.error(`❌ Layout not found: ${slide.layout} in group ${slide.layout_group}`);
        
        // Try to render with a basic fallback layout that can handle any content
        return (
          <div className="w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video relative z-20 mx-auto overflow-hidden bg-white p-8">
            <div className="h-full flex flex-col justify-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                {slide.content?.title || slide.content?.header?.title || 'Slide Title'}
              </h1>
              {slide.content?.description && (
                <p className="text-lg text-gray-600 mb-6">
                  {slide.content.description}
                </p>
              )}
              {slide.content?.paragraph && (
                <p className="text-base text-gray-700">
                  {slide.content.paragraph}
                </p>
              )}
              {slide.content?.subtitle && (
                <p className="text-xl text-gray-500">
                  {slide.content.subtitle}
                </p>
              )}
              {/* Show any other content that might exist */}
              {slide.content && Object.keys(slide.content).length > 0 && (
                <div className="mt-4 p-4 bg-gray-50 rounded">
                  <p className="text-sm text-gray-500 mb-2">Available content:</p>
                  <pre className="text-xs text-gray-600 overflow-auto max-h-32">
                    {JSON.stringify(slide.content, null, 2)}
                  </pre>
                </div>
              )}
            </div>
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
      console.log(`🔍 Slide ${slide.index + 1} - Full slide object:`, slide);
      console.log(`🔍 Slide ${slide.index + 1} - Layout:`, slide.layout);
      console.log(`🔍 Slide ${slide.index + 1} - Layout Group:`, slide.layout_group);
      console.log(`🔍 Slide ${slide.index + 1} - Content:`, slide.content);
      console.log(`🔍 Slide ${slide.index + 1} - Content type:`, typeof slide.content);
      console.log(`🔍 Slide ${slide.index + 1} - Content keys:`, Object.keys(slide.content || {}));
      
      // Debug: Check if content is empty or malformed
      if (!slide.content || (typeof slide.content === 'object' && Object.keys(slide.content).length === 0)) {
        console.warn(`⚠️ Slide ${slide.index + 1} has empty or missing content!`);
        return (
          <div className="w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video relative z-20 mx-auto overflow-hidden bg-white p-8">
            <div className="h-full flex flex-col justify-center items-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                Slide {slide.index + 1}
              </h1>
              <p className="text-lg text-gray-600 mb-6">
                Content is being generated...
              </p>
              <div className="text-sm text-gray-500">
                Layout: {slide.layout} | Group: {slide.layout_group}
              </div>
            </div>
          </div>
        );
      }
      
      // Debug: Check if Layout component is actually loaded
      console.log(`🔍 Slide ${slide.index + 1} - Layout component:`, Layout);
      console.log(`🔍 Slide ${slide.index + 1} - Layout component type:`, typeof Layout);
      console.log(`🔍 Slide ${slide.index + 1} - Layout component name:`, Layout?.name || Layout?.displayName || 'Unknown');
      
      if (!Layout) {
        console.error(`❌ Layout component is null for slide ${slide.index + 1}`);
        console.error(`❌ Slide layout: ${slide.layout}, group: ${slide.layout_group}`);
        
        // Try to find any available layout as a fallback
        const fallbackLayouts = [
          'standard:heading-bullet-image-description-layout',
          'standard:icon-image-description-layout',
          'standard:intro-slide-layout',
          'standard:contact-layout',
          'standard:table-of-contents-layout'
        ];
        
        let fallbackLayout = null;
        for (const fallbackKey of fallbackLayouts) {
          const layout = getLayoutById(fallbackKey);
          if (layout) {
            fallbackLayout = getLayout(fallbackKey);
            console.log(`✅ Using fallback layout: ${fallbackKey}`);
            break;
          }
        }
        
        if (!fallbackLayout) {
          return (
            <div className="w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video relative z-20 mx-auto overflow-hidden bg-white p-8">
              <div className="h-full flex flex-col justify-center items-center">
                <h1 className="text-4xl font-bold text-red-600 mb-4">
                  Layout Component Not Loaded
                </h1>
                <p className="text-lg text-gray-600 mb-6">
                  Layout: {slide.layout} | Group: {slide.layout_group}
                </p>
                <div className="text-sm text-gray-500 mb-4">
                  Check console for detailed error information
                </div>
                <div className="text-xs text-gray-400 max-w-md">
                  <strong>Available content:</strong>
                  <pre className="mt-2 p-2 bg-gray-100 rounded text-left overflow-auto max-h-32">
                    {JSON.stringify(slide.content, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          );
        }
        
        // Use fallback layout
        Layout = fallbackLayout;
        
        // If still no layout found, create a basic fallback
        if (!Layout) {
          console.warn(`⚠️ No fallback layout found, creating basic fallback for slide ${slide.index + 1}`);
          Layout = ({ data }: { data: any }) => (
            <div className="w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video relative z-20 mx-auto overflow-hidden bg-white p-8">
              <div className="h-full flex flex-col justify-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  {data?.title || data?.heading || `Slide ${slide.index + 1}`}
                </h1>
                {data?.description && (
                  <p className="text-lg text-gray-600 mb-6">
                    {data.description}
                  </p>
                )}
                {data?.subheading && (
                  <p className="text-base text-gray-700">
                    {data.subheading}
                  </p>
                )}
                {data?.paragraph && (
                  <p className="text-base text-gray-700">
                    {data.paragraph}
                  </p>
                )}
                {data?.subtitle && (
                  <p className="text-xl text-gray-500">
                    {data.subtitle}
                  </p>
                )}
                {/* Show any other content that might exist */}
                {data && Object.keys(data).length > 0 && (
                  <div className="mt-4 p-4 bg-gray-50 rounded">
                    <p className="text-sm text-gray-500 mb-2">Available content:</p>
                    <pre className="text-xs text-gray-600 overflow-auto max-h-32">
                      {JSON.stringify(data, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          );
        }
      }
      
      // Transform content to match template expectations
      let transformedContent = slide.content;
      
      try {
      if (slide.content) {
          transformedContent = { ...slide.content };
          
          // Handle case where content might be a string that needs parsing
          if (typeof transformedContent === 'string') {
            try {
              transformedContent = JSON.parse(transformedContent);
            } catch (parseError) {
              console.warn(`⚠️ Could not parse slide content as JSON:`, parseError);
              transformedContent = { title: transformedContent };
            }
          }
          
          // Ensure we have a proper content structure
          if (!transformedContent || typeof transformedContent !== 'object') {
            transformedContent = { title: 'Untitled Slide' };
          }
          
          // Ensure image data is in the right format
          if (transformedContent.image && typeof transformedContent.image === 'string') {
            transformedContent.image = {
              __image_url__: transformedContent.image,
              __image_prompt__: transformedContent.title || 'Slide image'
            };
          }
          
          // Ensure media data is in the right format
          if (transformedContent.media && typeof transformedContent.media === 'string') {
            transformedContent.media = {
              type: 'image',
              image: {
                __image_url__: transformedContent.media,
                __image_prompt__: transformedContent.title || 'Slide media'
              }
            };
          }
          
          // Map common content fields to template structure
          if (transformedContent.title && !transformedContent.header?.title) {
            transformedContent.header = {
              ...transformedContent.header,
              title: transformedContent.title
            };
          }
          
          // Handle subtitle mapping
          if (transformedContent.subtitle && !transformedContent.header?.subtitle) {
            transformedContent.header = {
              ...transformedContent.header,
              subtitle: transformedContent.subtitle
            };
          }
          
          // Handle description mapping
          if (transformedContent.description && !transformedContent.body?.description) {
            transformedContent.body = {
              ...transformedContent.body,
              description: transformedContent.description
            };
          }
          
          // Map to template-specific fields
          if (transformedContent.title && !transformedContent.heading) {
            transformedContent.heading = transformedContent.title;
          }
          
          if (transformedContent.description && !transformedContent.subheading) {
            transformedContent.subheading = transformedContent.description;
          }
          
          // Ensure header structure exists
          if (!transformedContent.header) {
            transformedContent.header = {
              title: transformedContent.title || 'Untitled Slide',
              subtitle: transformedContent.subtitle || ''
            };
          }
          
          // Ensure body structure exists
          if (!transformedContent.body) {
            transformedContent.body = {
              description: transformedContent.description || ''
            };
          }
          
          // Handle bullet points if they exist
          if (transformedContent.bulletPoints && Array.isArray(transformedContent.bulletPoints)) {
            transformedContent.bulletPoints = transformedContent.bulletPoints.map((bullet: any) => {
              if (typeof bullet === 'string') {
                return {
                  text: bullet,
                  icon: {
                    __icon_url__: 'https://static.thenounproject.com/png/5563447-200.png',
                    __icon_query__: 'bullet point icon'
                  }
                };
              }
              return bullet;
            });
          }
          
          // Handle metrics if they exist
          if (transformedContent.metrics && Array.isArray(transformedContent.metrics)) {
            transformedContent.metrics = transformedContent.metrics.map((metric: any) => {
              if (typeof metric === 'string') {
                return {
                  label: metric,
                  value: 'N/A',
                  trend: 'stable'
                };
              }
              return metric;
            });
          }
          
          // Ensure introCard is properly structured
          if (transformedContent.introCard && typeof transformedContent.introCard === 'object') {
            transformedContent.introCard = {
              enabled: true,
              initials: transformedContent.introCard.initials || 'PD',
              name: transformedContent.introCard.name || 'Presentation Team',
              date: transformedContent.introCard.date || new Date().toLocaleDateString(),
              ...transformedContent.introCard
            };
          }
          
          // Final validation: ensure we have at least a title
          if (!transformedContent.title && !transformedContent.header?.title) {
            transformedContent.title = `Slide ${slide.index + 1}`;
            transformedContent.header = {
              ...transformedContent.header,
              title: transformedContent.title
            };
          }
          
          // Ensure we have the required fields for the template
          if (!transformedContent.heading) {
            transformedContent.heading = transformedContent.title || `Slide ${slide.index + 1}`;
          }
          
          if (!transformedContent.subheading) {
            transformedContent.subheading = transformedContent.description || 'Content is being generated...';
          }
          
          // Ensure we have a page number
          if (!transformedContent.pageNumber) {
            transformedContent.pageNumber = `${slide.index + 1}`;
          }
          
          // Ensure we have a title for display
          if (!transformedContent.title) {
            transformedContent.title = transformedContent.heading || `Slide ${slide.index + 1}`;
          }
          
          // Ensure we have a description for display
          if (!transformedContent.description) {
            transformedContent.description = transformedContent.subheading || 'Content is being generated...';
          }
          
          console.log(`🔍 Slide ${slide.index + 1} - Transformed content:`, transformedContent);
        } else {
          // If no content, create a basic structure
          transformedContent = {
            title: `Slide ${slide.index + 1}`,
            heading: `Slide ${slide.index + 1}`,
            subheading: 'Content is being generated...',
            pageNumber: `${slide.index + 1}`,
            header: {
              title: `Slide ${slide.index + 1}`,
              subtitle: ''
            },
            body: {
              description: 'Content is being generated...'
            }
          };
        }
      } catch (error) {
        console.error(`❌ Error transforming content for slide ${slide.index + 1}:`, error);
        // Create a fallback content structure
        transformedContent = {
          title: `Slide ${slide.index + 1}`,
          heading: `Slide ${slide.index + 1}`,
          subheading: 'Content is being generated...',
          pageNumber: `${slide.index + 1}`,
          header: {
            title: `Slide ${slide.index + 1}`,
            subtitle: ''
          },
          body: {
            description: 'Content is being generated...'
          }
        };
      }
      
      // Final debug: Check if Layout component is valid
      if (!Layout || typeof Layout !== 'function') {
        console.error(`❌ Slide ${slide.index + 1} - Layout component is invalid:`, Layout);
        return (
          <div className="w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video relative z-20 mx-auto overflow-hidden bg-white p-8">
            <div className="h-full flex flex-col justify-center items-center">
              <h1 className="text-4xl font-bold text-red-600 mb-4">
                Layout Component Invalid
              </h1>
              <p className="text-lg text-gray-600 mb-6">
                Layout: {slide.layout} | Group: {slide.layout_group}
              </p>
              <div className="text-sm text-gray-500 mb-4">
                Layout component type: {typeof Layout}
              </div>
              <div className="text-xs text-gray-400 max-w-md">
                <strong>Transformed content:</strong>
                <pre className="mt-2 p-2 bg-gray-100 rounded text-left overflow-auto max-h-32">
                  {JSON.stringify(transformedContent, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        );
      }

      // Try to render with the Layout component, but provide a fallback
      try {
        return (
          <SlideErrorBoundary label={`Slide ${slide.index + 1}`}>
            <Layout data={transformedContent} />
          </SlideErrorBoundary>
        );
      } catch (error) {
        console.error(`❌ Slide ${slide.index + 1} - Error rendering Layout component:`, error);
        // Fallback: Display content in a structured way
        return (
          <div className="w-full rounded-sm max-w-[1280px] shadow-lg max-h-[720px] aspect-video relative z-20 mx-auto overflow-hidden bg-white p-8">
            <div className="h-full flex flex-col justify-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                {transformedContent.title || transformedContent.heading || `Slide ${slide.index + 1}`}
              </h1>
              {transformedContent.description && (
                <p className="text-lg text-gray-600 mb-6">
                  {transformedContent.description}
                </p>
              )}
              {transformedContent.subheading && (
                <p className="text-base text-gray-700">
                  {transformedContent.subheading}
                </p>
              )}
              {transformedContent.paragraph && (
                <p className="text-base text-gray-700">
                  {transformedContent.paragraph}
                </p>
              )}
              {transformedContent.subtitle && (
                <p className="text-xl text-gray-500">
                  {transformedContent.subtitle}
                </p>
              )}
              {/* Show any other content that might exist */}
              {transformedContent && Object.keys(transformedContent).length > 0 && (
                <div className="mt-4 p-4 bg-gray-50 rounded">
                  <p className="text-sm text-gray-500 mb-2">Available content:</p>
                  <pre className="text-xs text-gray-600 overflow-auto max-h-32">
                    {JSON.stringify(transformedContent, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        );
      }
    };
  }, [getTemplateLayout, dispatch]);

  return {
    getTemplateLayout,
    renderSlideContent,
    loading,
  };
};
