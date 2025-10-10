"""
Improved LLM Client for slide content generation with enhanced JSON parsing
"""

import json
import re
from typing import Dict, Any, Optional
from services.llm_client import LLMClient

class ImprovedLLMClient:
    def __init__(self):
        self._llm_client = None
        self._provider = None
    
    @property
    def llm_client(self):
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client
    
    @property
    def provider(self):
        if self._provider is None:
            self._provider = self.llm_client.llm_provider.value
        return self._provider

    async def generate_slide_content(
        self,
        outline: str,
        language: str,
        tone: Optional[str] = None,
        verbosity: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate slide content using the improved LLM client"""
        try:
            if self.provider == "google":
                response = await self._generate_with_google(
                    outline=outline,
                    language=language,
                    tone=tone,
                    verbosity=verbosity,
                    instructions=instructions
                )
            elif self.provider == "openai":
                response = await self._generate_with_openai(
                    outline=outline,
                    language=language,
                    tone=tone,
                    verbosity=verbosity,
                    instructions=instructions
                )
            else:
                # Fallback to original LLM client
                response = await self.llm_client.generate_slide_content(
                    outline=outline,
                    language=language,
                    tone=tone,
                    verbosity=verbosity,
                    instructions=instructions
                )
            
            # Enhanced JSON parsing for responses
            if isinstance(response, str):
                try:
                    parsed_response = json.loads(response)
                    print(f"🔍 Response parsed successfully: {parsed_response}")
                    return parsed_response
                except json.JSONDecodeError:
                    # Try to extract JSON from the response
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        parsed_json = json.loads(json_match.group())
                        print(f"🔍 Extracted JSON from response: {parsed_json}")
                        return parsed_json
                    else:
                        raise ValueError(f"Failed to parse JSON response: {response}")
            else:
                return response
                
        except Exception as e:
            print(f"🔍 Error in improved LLM client: {str(e)}")
            # Fallback to original LLM client
            try:
                response = await self.llm_client.generate_slide_content(
                    outline=outline,
                    language=language,
                    tone=tone,
                    verbosity=verbosity,
                    instructions=instructions
                )
                # Try to parse the fallback response
                if isinstance(response, str):
                    try:
                        return json.loads(response)
                    except json.JSONDecodeError:
                        json_match = re.search(r'\{.*\}', response, re.DOTALL)
                        if json_match:
                            return json.loads(json_match.group())
                        else:
                            return {"error": str(e), "slides": []}
                return response
            except Exception as fallback_error:
                print(f"🔍 Fallback also failed: {str(fallback_error)}")
                return {"error": str(e), "slides": []}

    async def _generate_with_google(
        self,
        outline: str,
        language: str,
        tone: Optional[str] = None,
        verbosity: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> str:
        """Generate content using Google/Gemini with enhanced JSON parsing"""
        try:
            response = await self.llm_client.generate_slide_content(
                outline=outline,
                language=language,
                tone=tone,
                verbosity=verbosity,
                instructions=instructions
            )
            
            # Return the response as string for further processing
            return response
                
        except Exception as e:
            print(f"🔍 Error in Google generation: {str(e)}")
            raise e

    async def _generate_with_openai(
        self,
        outline: str,
        language: str,
        tone: Optional[str] = None,
        verbosity: Optional[str] = None,
        instructions: Optional[str] = None,
    ) -> str:
        """Generate content using OpenAI with enhanced JSON parsing"""
        try:
            response = await self.llm_client.generate_slide_content(
                outline=outline,
                language=language,
                tone=tone,
                verbosity=verbosity,
                instructions=instructions
            )
            
            # Return the response as string for further processing
            return response
                
        except Exception as e:
            print(f"🔍 Error in OpenAI generation: {str(e)}")
            raise e

# Create a global instance
improved_llm_client = ImprovedLLMClient()
