// Removed old header imports - now using fetchWithAuth from utils/api
import { IconSearch, ImageGenerate, ImageSearch, PreviousGeneratedImagesResponse } from "./params";
import { ApiResponseHandler } from "./api-error-handler";
import { fetchWithAuth, fetchWithAuthFormData } from "@/utils/api";

export class PresentationGenerationApi {
  static async uploadDoc(documents: File[]) {
    const formData = new FormData();

    documents.forEach((document) => {
      formData.append("files", document);
    });

    try {
      console.log('PresentationGenerationApi.uploadDoc: Starting document upload');
      
      const response = await fetchWithAuthFormData(
        `/api/v1/ppt/files/upload`,
        {
          method: "POST",
          body: formData,
          cache: "no-cache",
        }
      );

      console.log('PresentationGenerationApi.uploadDoc: Response status:', response.status);
      return await ApiResponseHandler.handleResponse(response, "Failed to upload documents");
    } catch (error) {
      console.error("Upload error:", error);
      throw error;
    }
  }

  static async decomposeDocuments(documentKeys: string[]) {
    try {
      console.log('PresentationGenerationApi.decomposeDocuments: Starting document decomposition');
      
      const response = await fetchWithAuth(
        `/api/v1/ppt/files/decompose`,
        {
          method: "POST",
          body: JSON.stringify({
            file_paths: documentKeys,
          }),
          cache: "no-cache",
        }
      );
      
      console.log('PresentationGenerationApi.decomposeDocuments: Response status:', response.status);
      return await ApiResponseHandler.handleResponse(response, "Failed to decompose documents");
    } catch (error) {
      console.error("Error in Decompose Files", error);
      throw error;
    }
  }
 
   static async createPresentation({
    content,
    n_slides,
    file_paths,
    language,
    tone,
    verbosity,
    instructions,
    include_table_of_contents,
    include_title_slide,
    web_search,
    
  }: {
    content: string;
    n_slides: number | null;
    file_paths?: string[];
    language: string | null;
    tone?: string | null;
    verbosity?: string | null;
    instructions?: string | null;
    include_table_of_contents?: boolean;
    include_title_slide?: boolean;
    web_search?: boolean;
  }) {
    try {
      console.log('PresentationGenerationApi.createPresentation: Starting presentation creation');
      
      const response = await fetchWithAuth(
        `/api/v1/ppt/presentation/create`,
        {
          method: "POST",
          body: JSON.stringify({
            content,
            n_slides,
            file_paths,
            language,
            tone,
            verbosity,
            instructions,
            include_table_of_contents,
            include_title_slide,
            web_search,
          }),
          cache: "no-cache",
        }
      );
      
      console.log('PresentationGenerationApi.createPresentation: Response status:', response.status);
      return await ApiResponseHandler.handleResponse(response, "Failed to create presentation");
    } catch (error) {
      console.error("error in presentation creation", error);
      throw error;
    }
  }

  static async editSlide(
    slide_id: string,
    prompt: string
  ) {
    try {
      const response = await fetchWithAuth(
        `/api/v1/ppt/slide/edit`,
        {
          method: "POST",
          body: JSON.stringify({
            id: slide_id,
            prompt,
          }),
          cache: "no-cache",
        }
      );

      return await ApiResponseHandler.handleResponse(response, "Failed to update slide");
    } catch (error) {
      console.error("error in slide update", error);
      throw error;
    }
  }

  static async updatePresentationContent(body: any) {
    try {
      const response = await fetchWithAuth(
        `/api/v1/ppt/presentation/update`,
        {
          method: "PATCH",
          body: JSON.stringify(body),
          cache: "no-cache",
        }
      );
      
      return await ApiResponseHandler.handleResponse(response, "Failed to update presentation content");
    } catch (error) {
      console.error("error in presentation content update", error);
      throw error;
    }
  }

  static async presentationPrepare(presentationData: any) {
    try {
      console.log('PresentationGenerationApi.presentationPrepare: Starting presentation preparation');
      
      const response = await fetchWithAuth(
        `/api/v1/ppt/presentation/prepare`,
        {
          method: "POST",
          body: JSON.stringify(presentationData),
          cache: "no-cache",
        }
      );
      
      console.log('PresentationGenerationApi.presentationPrepare: Response status:', response.status);
      return await ApiResponseHandler.handleResponse(response, "Failed to prepare presentation");
    } catch (error) {
      console.error("error in data generation", error);
      throw error;
    }
  }
  
  // IMAGE AND ICON SEARCH
  
  
  static async generateImage(imageGenerate: ImageGenerate) {
    try {
      const response = await fetchWithAuth(
        `/api/v1/ppt/images/generate?prompt=${imageGenerate.prompt}`,
        {
          method: "GET",
          cache: "no-cache",
        }
      );
      
      return await ApiResponseHandler.handleResponse(response, "Failed to generate image");
    } catch (error) {
      console.error("error in image generation", error);
      throw error;
    }
  }

  static getPreviousGeneratedImages = async (): Promise<PreviousGeneratedImagesResponse[]> => {
    try {
      const response = await fetchWithAuth(
        `/api/v1/ppt/images/generated`,
        {
          method: "GET",
        }
      );
      
      return await ApiResponseHandler.handleResponse(response, "Failed to get previous generated images");
    } catch (error) {
      console.error("error in getting previous generated images", error);
      throw error;
    }
  }
  
  static async searchIcons(iconSearch: IconSearch) {
    try {
      const response = await fetchWithAuth(
        `/api/v1/ppt/icons/search?query=${iconSearch.query}&limit=${iconSearch.limit}`,
        {
          method: "GET",
          cache: "no-cache",
        }
      );
      
      return await ApiResponseHandler.handleResponse(response, "Failed to search icons");
    } catch (error) {
      console.error("error in icon search", error);
      throw error;
    }
  }



  // EXPORT PRESENTATION
  static async exportAsPPTX(presentationData: any) {
    try {
      const response = await fetchWithAuth(
        `/api/v1/ppt/presentation/export/pptx`,
        {
          method: "POST",
          body: JSON.stringify(presentationData),
          cache: "no-cache",
        }
      );
      return await ApiResponseHandler.handleResponse(response, "Failed to export as PowerPoint");
    } catch (error) {
      console.error("error in pptx export", error);
      throw error;
    }
  }
  
  

}