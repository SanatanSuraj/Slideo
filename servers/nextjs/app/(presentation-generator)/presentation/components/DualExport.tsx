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
import { fetchWithAuth } from "@/utils/api";

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

      // Call the FastAPI export endpoint for PDF
      const response = await fetchWithAuth('/api/v1/ppt/export/presentation', {
        method: 'POST',
        body: JSON.stringify({
          presentation_id: presentation_id,
          title: presentationData.title || 'Presentation',
          export_as: 'pdf',
          save_final_edit: true
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to export PDF');
      }

      const result = await response.json();
      
      if (result.success && result.presentation_and_path?.s3_pdf_url) {
        // Download the PDF file
        const pdfUrl = result.presentation_and_path.s3_pdf_url;
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = `${presentationData.title || 'presentation'}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        toast.success("PDF exported successfully!");
      } else {
        throw new Error('Export response did not contain valid PDF URL');
      }
      
    } catch (error) {
      console.error("PDF export error:", error);
      toast.error("Failed to export PDF", {
        description: error instanceof Error ? error.message : "There was an error exporting your presentation as PDF. Please try again."
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

      // Call the FastAPI export endpoint for PPTX
      const response = await fetchWithAuth('/api/v1/ppt/export/presentation', {
        method: 'POST',
        body: JSON.stringify({
          presentation_id: presentation_id,
          title: presentationData.title || 'Presentation',
          export_as: 'pptx',
          save_final_edit: true
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to export PPTX');
      }

      const result = await response.json();
      
      if (result.success && result.presentation_and_path?.s3_pptx_url) {
        // Download the PPTX file
        let pptxUrl = result.presentation_and_path.s3_pptx_url;
        
        // If it's a relative URL, construct the full FastAPI URL
        if (pptxUrl.startsWith('/api/')) {
          const fastApiBaseUrl = process.env.NEXT_PUBLIC_FASTAPI_BASE_URL || 'http://localhost:8000';
          pptxUrl = `${fastApiBaseUrl}${pptxUrl}`;
        }
        
        // Create download link directly (token is already in the URL)
        const link = document.createElement('a');
        link.href = pptxUrl;
        link.download = `${presentationData.title || 'presentation'}.pptx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        toast.success("PPTX exported successfully!");
      } else {
        throw new Error('Export response did not contain valid PPTX URL');
      }
      
    } catch (error) {
      console.error("PPTX export error:", error);
      toast.error("Failed to export PPTX", {
        description: error instanceof Error ? error.message : "There was an error exporting your presentation as PPTX. Please try again."
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
