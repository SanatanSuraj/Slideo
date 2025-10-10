'use client'
import { useEffect, useRef, useCallback, useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { PresentationGenerationApi } from '../../services/api/presentation-generation';
import { addToHistory } from '@/store/slices/undoRedoSlice';

interface UseAutoSaveOptions {
    debounceMs?: number;
    enabled?: boolean;
}

export const useAutoSave = ({
    debounceMs = 1000,
    enabled = true,
}: UseAutoSaveOptions = {}) => {
   
    const dispatch = useDispatch();
    const { presentationData, isStreaming, isLoading, isLayoutLoading } = useSelector(
        (state: RootState) => state.presentationGeneration
    );

    const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const lastSavedDataRef = useRef<string>('');
    const [isSaving, setIsSaving] = useState<boolean>(false);
 

    // Debounced save function
    const debouncedSave = useCallback(async (data: any) => {
        // Clear existing timeout
        if (saveTimeoutRef.current) {
            clearTimeout(saveTimeoutRef.current);
        }

        // Set new timeout
        saveTimeoutRef.current = setTimeout(async () => {
            if (!data || isSaving) return;

            const currentDataString = JSON.stringify(data);

            // Skip if data hasn't changed since last save
            if (currentDataString === lastSavedDataRef.current) {
                return;
            }

            try {
                setIsSaving(true);
                console.log('🔄 Auto-saving presentation data...', {
                    presentationId: data?.id,
                    slidesCount: data?.slides?.length,
                    timestamp: new Date().toISOString()
                });

                // Call the API to update presentation content
                const response = await PresentationGenerationApi.updatePresentationContent(data);

                // Update last saved data reference
                lastSavedDataRef.current = currentDataString;

                console.log('✅ Auto-save successful', {
                    presentationId: data?.id,
                    response: response
                });

            } catch (error) {
                console.error('❌ Auto-save failed:', {
                    error: error,
                    presentationId: data?.id,
                    slidesCount: data?.slides?.length,
                    timestamp: new Date().toISOString()
                });

                // Show user-friendly error message
                if (error instanceof Error) {
                    console.error('Auto-save error details:', error.message);
                }

            } finally {
                setIsSaving(false);
            }
        }, debounceMs);
    }, [debounceMs, isSaving]);

    // Effect to trigger auto-save when presentation data changes
    useEffect(() => {
        if (!enabled || !presentationData || isStreaming || isLoading) return;
        
        dispatch(addToHistory({
            slides: presentationData.slides,
            actionType: "AUTO_SAVE"
        }));
        // Trigger debounced save
        debouncedSave(presentationData);
       
        // Cleanup timeout on unmount
        return () => {
            if (saveTimeoutRef.current) {
                clearTimeout(saveTimeoutRef.current);
            }
        };
    }, [presentationData, enabled, debouncedSave, isLoading, isStreaming]);
    
    // Manual save function for fallback
    const manualSave = useCallback(async () => {
        if (!presentationData || isSaving) return;
        
        try {
            setIsSaving(true);
            console.log('🔄 Manual save triggered...');
            
            const response = await PresentationGenerationApi.updatePresentationContent(presentationData);
            
            // Update last saved data reference
            lastSavedDataRef.current = JSON.stringify(presentationData);
            
            console.log('✅ Manual save successful');
            return response;
        } catch (error) {
            console.error('❌ Manual save failed:', error);
            throw error;
        } finally {
            setIsSaving(false);
        }
    }, [presentationData, isSaving]);

    return {
        isSaving,
        manualSave,
    };
}; 