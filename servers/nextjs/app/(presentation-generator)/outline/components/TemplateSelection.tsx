"use client";
import React, { useEffect } from "react";
import { useLayout } from "../../context/LayoutContext";
import TemplateLayouts from "./TemplateLayouts";

import { Template } from "../types/index";

import { fetchWithAuthWait } from "@/utils/api";
interface TemplateSelectionProps {
  selectedTemplate: Template | null;
  onSelectTemplate: (template: Template) => void;
}

const TemplateSelection: React.FC<TemplateSelectionProps> = ({
  selectedTemplate,
  onSelectTemplate
}) => {
  const {
    getLayoutsByTemplateID,
    getTemplateSetting,
    getAllTemplateIDs,
    getFullDataByTemplateID,
    loading,
    getAllLayouts
  } = useLayout();

  const [summaryMap, setSummaryMap] = React.useState<Record<string, { lastUpdatedAt?: number; name?: string; description?: string }>>({});

  useEffect(() => {
    // Fetch custom templates summary to get last_updated_at and template meta for sorting and display
    const fetchSummary = async () => {
      try {
        const res = await fetchWithAuthWait(`/api/v1/ppt/template-management/summary`);
        
        if (res.status === 401) {
          console.warn('TemplateSelection: 401 Unauthorized - user may not be authenticated yet');
          setSummaryMap({});
          return;
        }
        
        if (!res.ok) {
          console.error('TemplateSelection: Failed to fetch template summary:', res.status);
          setSummaryMap({});
          return;
        }
        
        const data = await res.json();
        const map: Record<string, { lastUpdatedAt?: number; name?: string; description?: string }> = {};
        if (data && Array.isArray(data.presentations)) {
          for (const p of data.presentations) {
            const slug = `custom-${p.presentation_id}`;
            map[slug] = {
              lastUpdatedAt: p.last_updated_at ? new Date(p.last_updated_at).getTime() : 0,
              name: p.template?.name,
              description: p.template?.description,
            };
          }
        }
        setSummaryMap(map);
      } catch (error) {
        console.error('TemplateSelection: Error fetching template summary:', error);
        setSummaryMap({});
      }
    };
    
    fetchSummary();
  }, []);

  const templates: Template[] = React.useMemo(() => {
    const templates = getAllTemplateIDs();
    console.log('🔍 TemplateSelection - getAllTemplateIDs():', templates);
    console.log('🔍 TemplateSelection - loading:', loading);
    
    // Debug: Check what layouts are available for each template
    templates.forEach(templateId => {
      const layouts = getLayoutsByTemplateID(templateId);
      console.log(`🔍 TemplateSelection - Template ${templateId} has ${layouts.length} layouts:`, layouts);
    });
    
    if (templates.length === 0) {
      console.log('🔍 TemplateSelection - No templates found, returning empty array');
      return [];
    }

    const Templates: Template[] = templates
      .filter((templateID: string) => {
        // Filter out template that contain any errored layouts (from custom templates compile/parse errors)
        const fullData = getFullDataByTemplateID(templateID);
        const hasErroredLayouts = fullData.some((fd: any) => (fd as any)?.component?.displayName === "CustomTemplateErrorSlide");
        console.log(`🔍 TemplateSelection - Template ${templateID}: hasErroredLayouts=${hasErroredLayouts}, fullData length=${fullData.length}`);
        return !hasErroredLayouts;
      })
      .map(templateID => {
        const settings = getTemplateSetting(templateID);
        const customMeta = summaryMap[templateID];
        const isCustom = templateID.toLowerCase().startsWith("custom-");
        return {
          id: templateID,
          name: isCustom && customMeta?.name ? customMeta.name : templateID,
          description: (isCustom && customMeta?.description) ? customMeta.description : (settings?.description || `${templateID} presentation templates`),
          ordered: settings?.ordered || false,
          default: settings?.default || false,
        };
      });

    // Sort templates to put default first, then by name
    const sortedTemplates = Templates.sort((a, b) => {
      if (a.default && !b.default) return -1;
      if (!a.default && b.default) return 1;
      return a.name.localeCompare(b.name);
    });
    
    console.log('🔍 TemplateSelection - Final templates:', sortedTemplates);
    return sortedTemplates;
  }, [getAllTemplateIDs, getLayoutsByTemplateID, getTemplateSetting, getFullDataByTemplateID, summaryMap, loading]);

  const inBuiltTemplates = React.useMemo(
    () => templates.filter(g => !g.id.toLowerCase().startsWith("custom-")),
    [templates]
  );
  const customTemplates = React.useMemo(() => {
    const unsorted = templates.filter(g => g.id.toLowerCase().startsWith("custom-"));
    // Sort by last_updated_at desc using summaryMap keyed by template id
    return unsorted.sort((a, b) => (summaryMap[b.id]?.lastUpdatedAt || 0) - (summaryMap[a.id]?.lastUpdatedAt || 0));
  }, [templates, summaryMap]);

  // Auto-select first template when templates are loaded
  useEffect(() => {
    if (templates.length > 0 && !selectedTemplate && !loading) {
      const defaultTemplate = templates.find(g => g.default) || templates[0];
      const slides = getLayoutsByTemplateID(defaultTemplate.id);
      console.log('🔍 TemplateSelection - Auto-selection:', {
        defaultTemplateId: defaultTemplate.id,
        defaultTemplateName: defaultTemplate.name,
        slidesCount: slides.length,
        slides: slides,
        loading: loading
      });

      // Use handleTemplateSelection for auto-selection to ensure proper validation
      handleTemplateSelection(defaultTemplate);
    }
  }, [templates, selectedTemplate, loading]);
  useEffect(() => {
    if (loading) {
      return;
    }
    const existingScript = document.querySelector(
      'script[src*="tailwindcss.com"]'
    );
    if (!existingScript) {
      const script = document.createElement("script");
      script.src = "https://cdn.tailwindcss.com";
      script.async = true;
      document.head.appendChild(script);
    }

  }, []);


  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="p-4 rounded-lg border border-gray-200 bg-gray-50 animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-3 bg-gray-200 rounded mb-3"></div>
              <div className="grid grid-cols-3 gap-2 mb-3">
                {[1, 2, 3].map((j) => (
                  <div key={j} className="aspect-video bg-gray-200 rounded"></div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (templates.length === 0) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <h5 className="text-lg font-medium mb-2 text-gray-700">
            No Templates Available
          </h5>
          <p className="text-gray-600 text-sm">
            No presentation templates could be loaded. Please try refreshing the page.
          </p>
        </div>
      </div>
    );
  }

  const handleTemplateSelection = (template: Template) => {
    console.log('🔍 TemplateSelection - handleTemplateSelection called:', {
      templateId: template.id,
      templateName: template.name,
      loading: loading
    });
    
    // Check if layout data is loaded
    if (loading) {
      console.warn('🔍 TemplateSelection - Layout data still loading, cannot select template yet');
      return;
    }
    
    // Check if we have any layouts loaded at all
    const allLayouts = getAllLayouts();
    if (allLayouts.length === 0) {
      console.warn('🔍 TemplateSelection - No layouts loaded yet, cannot select template');
      return;
    }
    
    const slides = getLayoutsByTemplateID(template.id);
    console.log('🔍 TemplateSelection - handleTemplateSelection:', {
      templateId: template.id,
      templateName: template.name,
      slidesCount: slides.length,
      slides: slides,
      loading: loading,
      totalLayouts: allLayouts.length
    });
    
    // Always call onSelectTemplate, even if slides.length is 0
    // This ensures the template is visually selected
    onSelectTemplate({
      ...template,
      slides: slides,
    });
    
    // If no slides found, try to get them again after a short delay
    if (slides.length === 0) {
      console.warn('🔍 TemplateSelection - No slides found, retrying after delay...');
      setTimeout(() => {
        const retrySlides = getLayoutsByTemplateID(template.id);
        console.log('🔍 TemplateSelection - Retry result:', {
          templateId: template.id,
          slidesCount: retrySlides.length,
          slides: retrySlides
        });
        
        // Update the template with the retry slides
        onSelectTemplate({
          ...template,
          slides: retrySlides,
        });
        
        // If still no slides, try one more time with a longer delay
        if (retrySlides.length === 0) {
          console.warn('🔍 TemplateSelection - Still no slides found, trying again with longer delay...');
          setTimeout(() => {
            const finalRetrySlides = getLayoutsByTemplateID(template.id);
            console.log('🔍 TemplateSelection - Final retry result:', {
              templateId: template.id,
              slidesCount: finalRetrySlides.length,
              slides: finalRetrySlides
            });
            onSelectTemplate({
              ...template,
              slides: finalRetrySlides,
            });
          }, 500);
        }
      }, 100);
    }
  }

  return (
    <div className="space-y-8 mb-4">
      {/* In Built Templates */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">In Built Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {inBuiltTemplates.map((template) => (
            <TemplateLayouts
              key={template.id}
              template={template}
              onSelectTemplate={handleTemplateSelection}
              selectedTemplate={selectedTemplate}
            />
          ))}
        </div>
      </div>

      {/* Custom AI Templates */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">Custom AI Templates</h3>
        </div>
        {customTemplates.length === 0 ? (
          <div className="text-sm text-gray-600 py-2">
            No custom templates. Create one from "All Templates" menu.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {customTemplates.map((template) => (
              <TemplateLayouts
                key={template.id}
                template={template}
                onSelectTemplate={handleTemplateSelection}
                selectedTemplate={selectedTemplate}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TemplateSelection; 