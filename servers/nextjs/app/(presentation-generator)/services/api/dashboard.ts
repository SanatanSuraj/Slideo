import {
  getHeader,
} from "@/app/(presentation-generator)/services/api/header";
import { ApiResponseHandler } from "@/app/(presentation-generator)/services/api/api-error-handler";
import { fetchWithAuth } from "@/utils/api";

export interface PresentationResponse {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  data: any | null;
  file: string;
  n_slides: number;
  prompt: string;
  summary: string | null;
    theme: string;
    titles: string[];
    user_id: string;
    vector_store: any;

    thumbnail: string;
    slides: any[];
}

export class DashboardApi {

  static async getPresentations(): Promise<PresentationResponse[]> {
    try {
      console.log('DashboardApi.getPresentations: Starting to fetch presentations');
      
      const response = await fetchWithAuth(
        `/api/v1/ppt/presentation/all`,
        {
          method: "GET",
        }
      );
      
      console.log('DashboardApi.getPresentations: Response status:', response.status);
      console.log('DashboardApi.getPresentations: Response headers:', Object.fromEntries(response.headers.entries()));
      
      // Handle the special case where 404 means "no presentations found"
      if (response.status === 404) {
        console.log("No presentations found - returning empty array");
        return [];
      }
      
      const data = await ApiResponseHandler.handleResponse(response, "Failed to fetch presentations");
      console.log('DashboardApi.getPresentations: Successfully fetched presentations:', {
        count: data?.length || 0,
        presentations: data?.map(p => ({ id: p.id, title: p.title, updated_at: p.updated_at })) || []
      });
      
      return data;
    } catch (error) {
      console.error("Error fetching presentations:", {
        error: error,
        errorMessage: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : undefined
      });
      throw error;
    }
  }
  
  static async getPresentation(id: string) {
    try {
      console.log('DashboardApi.getPresentation: Starting to fetch presentation:', id);
      
      const response = await fetchWithAuth(
        `/api/v1/ppt/presentation/${id}`,
        {
          method: "GET",
        }
      );
      
      console.log('DashboardApi.getPresentation: Response status:', response.status);
      return await ApiResponseHandler.handleResponse(response, "Presentation not found");
    } catch (error) {
      console.error("Error fetching presentation:", error);
      throw error;
    }
  }
  
  static async deletePresentation(presentation_id: string) {
    try {
      console.log('DashboardApi.deletePresentation: Starting to delete presentation:', presentation_id);
      
      const response = await fetchWithAuth(
        `/api/v1/ppt/presentation/${presentation_id}`,
        {
          method: "DELETE",
        }
      );

      console.log('DashboardApi.deletePresentation: Response status:', response.status);
      return await ApiResponseHandler.handleResponseWithResult(response, "Failed to delete presentation");
    } catch (error) {
      console.error("Error deleting presentation:", error);
      return {
        success: false,
        message: error instanceof Error ? error.message : "Failed to delete presentation",
      };
    }
  }
}
