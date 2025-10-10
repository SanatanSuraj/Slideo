"use client";
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Download, FileText, Presentation } from "lucide-react";
import { toast } from "sonner";
import { useSelector } from "react-redux";
import { RootState } from "@/store/store";
import { PresentationGenerationApi } from "../../services/api/presentation-generation";
import { trackEvent, MixpanelEvent } from "@/utils/mixpanel";
import { usePathname } from "next/navigation";

// Note: Libraries are imported dynamically to avoid SSR issues

interface DualExportProps {
  presentation_id: string;
  onExportStart?: () => void;
  onExportEnd?: () => void;
}

const DualExport: React.FC<DualExportProps> = ({ 
  presentation_id, 
  onExportStart, 
  onExportEnd 
}) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportType, setExportType] = useState<'pdf' | 'pptx' | null>(null);
  const [isClient, setIsClient] = useState(false);
  const pathname = usePathname();

  // Ensure component only renders on client side
  React.useEffect(() => {
    setIsClient(true);
  }, []);

  const { presentationData, isStreaming } = useSelector(
    (state: RootState) => state.presentationGeneration
  );

  const downloadFile = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const exportAsPDF = async () => {
    if (isStreaming || !presentationData) return;

    try {
      setIsExporting(true);
      setExportType('pdf');
      onExportStart?.();

      // Save the presentation data before exporting
      trackEvent(MixpanelEvent.Header_UpdatePresentationContent_API_Call);
      await PresentationGenerationApi.updatePresentationContent(presentationData);

      trackEvent(MixpanelEvent.Header_ExportAsPDF_API_Call);

      // Check if we're in browser environment
      if (typeof window === 'undefined') {
        throw new Error('PDF export is only available in browser environment');
      }

      // Get the presentation slides wrapper element
      const slidesWrapper = document.getElementById('presentation-slides-wrapper');
      if (!slidesWrapper) {
        throw new Error('Presentation slides not found');
      }

      // Dynamically import html2pdf to avoid SSR issues
      const html2pdf = (await import('html2pdf.js')).default;

      // Configure html2pdf options
      const opt = {
        margin: 0,
        filename: `${presentationData.title || 'presentation'}.pdf`,
        image: { type: 'jpeg' as const, quality: 0.98 },
        html2canvas: { 
          scale: 2,
          useCORS: true,
          allowTaint: true,
          backgroundColor: '#ffffff'
        },
        jsPDF: { 
          unit: 'in', 
          format: 'a4', 
          orientation: 'landscape' 
        }
      };

      // Generate PDF
      const pdfBlob = await html2pdf().set(opt).from(slidesWrapper).outputPdf('blob');
      
      // Download the PDF
      downloadFile(pdfBlob, `${presentationData.title || 'presentation'}.pdf`);
      
      toast.success("PDF exported successfully!");
      
    } catch (error) {
      console.error("PDF export error:", error);
      toast.error("Failed to export PDF", {
        description: "There was an error exporting your presentation as PDF. Please try again."
      });
    } finally {
      setIsExporting(false);
      setExportType(null);
      onExportEnd?.();
    }
  };

  const exportAsPPTX = async () => {
    if (isStreaming || !presentationData) return;

    try {
      setIsExporting(true);
      setExportType('pptx');
      onExportStart?.();

      // Save the presentation data before exporting
      trackEvent(MixpanelEvent.Header_UpdatePresentationContent_API_Call);
      await PresentationGenerationApi.updatePresentationContent(presentationData);

      trackEvent(MixpanelEvent.Header_ExportAsPPTX_API_Call);

      // Check if we're in browser environment
      if (typeof window === 'undefined') {
        throw new Error('PPTX export is only available in browser environment');
      }

      // Dynamically import PptxGenJS to avoid SSR issues
      const PptxGenJS = (await import('pptxgenjs')).default;

      // Create a new presentation
      const pptx = new PptxGenJS();
      
      // Set presentation properties
      pptx.author = "PresentOn";
      pptx.company = "PresentOn";
      pptx.title = presentationData.title || "Presentation";
      pptx.subject = "Generated Presentation";

      // Process each slide
      for (let i = 0; i < presentationData.slides.length; i++) {
        const slide = presentationData.slides[i];
        const pptxSlide = pptx.addSlide();

        // Set slide background
        pptxSlide.background = { color: "FFFFFF" };

        // Parse slide content
        let slideContent;
        try {
          slideContent = typeof slide.content === 'string' 
            ? JSON.parse(slide.content) 
            : slide.content;
        } catch {
          slideContent = { type: 'text', content: slide.content || '' };
        }

        // Handle different slide types
        if (slideContent.type === 'title') {
          // Title slide
          pptxSlide.addText(slideContent.title || 'Title', {
            x: 1,
            y: 2,
            w: 8,
            h: 1.5,
            fontSize: 44,
            bold: true,
            color: "363636",
            align: "center",
            valign: "middle"
          });

          if (slideContent.subtitle) {
            pptxSlide.addText(slideContent.subtitle, {
              x: 1,
              y: 3.8,
              w: 8,
              h: 1,
              fontSize: 24,
              color: "666666",
              align: "center",
              valign: "middle"
            });
          }
        } else if (slideContent.type === 'content') {
          // Content slide
          if (slideContent.title) {
            pptxSlide.addText(slideContent.title, {
              x: 0.5,
              y: 0.5,
              w: 9,
              h: 0.8,
              fontSize: 32,
              bold: true,
              color: "363636"
            });
          }

          // Add bullet points
          if (slideContent.bullets && Array.isArray(slideContent.bullets)) {
            slideContent.bullets.forEach((bullet: string, index: number) => {
              pptxSlide.addText(`• ${bullet}`, {
                x: 0.5,
                y: 1.5 + (index * 0.6),
                w: 9,
                h: 0.5,
                fontSize: 18,
                color: "363636"
              });
            });
          }
        } else if (slideContent.type === 'image') {
          // Image slide
          if (slideContent.title) {
            pptxSlide.addText(slideContent.title, {
              x: 0.5,
              y: 0.5,
              w: 9,
              h: 0.8,
              fontSize: 32,
              bold: true,
              color: "363636",
              align: "center"
            });
          }

          if (slideContent.imageUrl) {
            try {
              pptxSlide.addImage({
                data: slideContent.imageUrl,
                x: 2,
                y: 2,
                w: 6,
                h: 4
              });
            } catch (imageError) {
              console.warn("Could not add image to slide:", imageError);
            }
          }
        } else {
          // Generic text slide
          const textContent = typeof slideContent === 'string' 
            ? slideContent 
            : slideContent.content || JSON.stringify(slideContent);
          
          pptxSlide.addText(textContent, {
            x: 0.5,
            y: 1,
            w: 9,
            h: 5,
            fontSize: 20,
            color: "363636",
            valign: "top"
          });
        }

        // Add slide number
        pptxSlide.addText(`${i + 1}`, {
          x: 9.2,
          y: 6.8,
          w: 0.5,
          h: 0.3,
          fontSize: 12,
          color: "999999",
          align: "right"
        });
      }

      // Generate and download the PPTX
      const pptxBlob = await pptx.writeFile();
      downloadFile(pptxBlob as Blob, `${presentationData.title || 'presentation'}.pptx`);
      
      toast.success("PPTX exported successfully!");
      
    } catch (error) {
      console.error("PPTX export error:", error);
      toast.error("Failed to export PPTX", {
        description: "There was an error exporting your presentation as PPTX. Please try again."
      });
    } finally {
      setIsExporting(false);
      setExportType(null);
      onExportEnd?.();
    }
  };

  const isDisabled = isStreaming || !presentationData || isExporting || !isClient;

  // Don't render until client-side hydration is complete
  if (!isClient) {
    return (
      <div className="flex flex-col gap-2">
        <Button
          disabled={true}
          variant="ghost"
          className="w-full flex justify-start text-[#5146E5] hover:bg-gray-50"
        >
          <FileText className="w-5 h-5 mr-3" />
          Export as PDF
        </Button>
        
        <Button
          disabled={true}
          variant="ghost"
          className="w-full flex justify-start text-[#5146E5] hover:bg-gray-50"
        >
          <Presentation className="w-5 h-5 mr-3" />
          Export as PPTX
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      <Button
        onClick={exportAsPDF}
        disabled={isDisabled}
        variant="ghost"
        className="w-full flex justify-start text-[#5146E5] hover:bg-gray-50"
      >
        <FileText className="w-5 h-5 mr-3" />
        {isExporting && exportType === 'pdf' ? 'Exporting PDF...' : 'Export as PDF'}
      </Button>
      
      <Button
        onClick={exportAsPPTX}
        disabled={isDisabled}
        variant="ghost"
        className="w-full flex justify-start text-[#5146E5] hover:bg-gray-50"
      >
        <Presentation className="w-5 h-5 mr-3" />
        {isExporting && exportType === 'pptx' ? 'Exporting PPTX...' : 'Export as PPTX'}
      </Button>
    </div>
  );
};

export default DualExport;
