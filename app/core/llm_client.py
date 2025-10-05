"""
Unified LLM Client for Presenton
Manages LLM provider logic dynamically based on environment configuration.
"""

import os
from typing import Optional, AsyncGenerator, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get LLM provider from environment
LLM_PROVIDER = os.getenv("LLM", "google").lower()

# Initialize clients based on provider
if LLM_PROVIDER == "google":
    import google.generativeai as genai
    
    # Configure Gemini API
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required for Google provider")
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    class LLMClient:
        def __init__(self):
            self.provider = "google"
            self.model = "gemini-2.0-flash"
        
        async def generate_outline(self, prompt: str, max_tokens: Optional[int] = None) -> str:
            """Generate outline using Gemini"""
            model = genai.GenerativeModel(self.model)
            try:
                response = model.generate_content(prompt)
                text = getattr(response, "text", "").strip()
                
                if not text:
                    print("⚠️ Gemini returned empty output:", response)
                    return '{"error": "Empty response from Gemini"}'
                
                # Attempt to parse JSON
                try:
                    import json
                    json.loads(text)
                    return text  # Return as-is if valid JSON
                except json.JSONDecodeError:
                    # Return as plain text outline if not JSON
                    print("🧠 Gemini returned plain text, wrapping in JSON structure")
                    return json.dumps({"outline": text})
                    
            except Exception as e:
                print("❌ Gemini generation error:", str(e))
                return json.dumps({"error": str(e)})
        
        async def generate_structured(self, prompt: str, response_format: Dict[str, Any], max_tokens: Optional[int] = None) -> Dict[str, Any]:
            """Generate structured content using Gemini"""
            model = genai.GenerativeModel(self.model)
            
            # Add JSON schema instruction to prompt
            structured_prompt = f"""
            {prompt}
            
            Please respond with valid JSON that matches this schema:
            {response_format}
            """
            
            try:
                response = model.generate_content(structured_prompt)
                text = getattr(response, "text", "").strip()
                
                if not text:
                    print("⚠️ Gemini returned empty output for structured generation:", response)
                    return {"error": "Empty response from Gemini"}
                
                # Try to extract JSON from response
                import json
                import re
                
                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass
                
                # If no JSON found, try to parse the entire response
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    # Return a basic structure if JSON parsing fails
                    print("🧠 Gemini returned plain text for structured generation, wrapping in basic structure")
                    return {"content": text}
                    
            except Exception as e:
                print("❌ Gemini structured generation error:", str(e))
                return {"error": str(e)}
        
        async def stream_outline(self, prompt: str, max_tokens: Optional[int] = None) -> AsyncGenerator[str, None]:
            """Stream outline generation using Gemini"""
            model = genai.GenerativeModel(self.model)
            
            try:
                # Gemini doesn't have native streaming for text generation
                # We'll simulate streaming by generating and yielding chunks
                response = model.generate_content(prompt)
                text = getattr(response, "text", "").strip()
                
                if not text:
                    print("⚠️ Gemini returned empty output for streaming:", response)
                    yield '{"error": "Empty response from Gemini"}'
                    return
                
                # Split into chunks for streaming effect
                chunk_size = 50
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i + chunk_size]
                    yield chunk
                    # Small delay to simulate streaming
                    import asyncio
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                print("❌ Gemini streaming error:", str(e))
                import json
                yield json.dumps({"error": str(e)})
        
        async def stream_structured(self, prompt: str, response_format: Dict[str, Any], max_tokens: Optional[int] = None) -> AsyncGenerator[str, None]:
            """Stream structured content generation using Gemini"""
            model = genai.GenerativeModel(self.model)
            
            # Add JSON schema instruction to prompt
            structured_prompt = f"""
            {prompt}
            
            Please respond with valid JSON that matches this schema:
            {response_format}
            """
            
            try:
                response = model.generate_content(structured_prompt)
                text = getattr(response, "text", "").strip()
                
                if not text:
                    print("⚠️ Gemini returned empty output for structured streaming:", response)
                    yield '{"error": "Empty response from Gemini"}'
                    return
                
                # Stream the JSON response
                chunk_size = 50
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i + chunk_size]
                    yield chunk
                    # Small delay to simulate streaming
                    import asyncio
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                print("❌ Gemini structured streaming error:", str(e))
                import json
                yield json.dumps({"error": str(e)})

elif LLM_PROVIDER == "openai":
    from openai import AsyncOpenAI
    
    # Configure OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")
    
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    class LLMClient:
        def __init__(self):
            self.provider = "openai"
            self.model = "gpt-4o-mini"
        
        async def generate_outline(self, prompt: str, max_tokens: Optional[int] = None) -> str:
            """Generate outline using OpenAI"""
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens or 4000
            )
            return response.choices[0].message.content.strip()
        
        async def generate_structured(self, prompt: str, response_format: Dict[str, Any], max_tokens: Optional[int] = None) -> Dict[str, Any]:
            """Generate structured content using OpenAI"""
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=max_tokens or 4000
            )
            
            import json
            return json.loads(response.choices[0].message.content)
        
        async def stream_outline(self, prompt: str, max_tokens: Optional[int] = None) -> AsyncGenerator[str, None]:
            """Stream outline generation using OpenAI"""
            stream = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens or 4000,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        async def stream_structured(self, prompt: str, response_format: Dict[str, Any], max_tokens: Optional[int] = None) -> AsyncGenerator[str, None]:
            """Stream structured content generation using OpenAI"""
            stream = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=max_tokens or 4000,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

else:
    raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}. Supported providers: google, openai")

# Create a global instance
llm_client = LLMClient()

# Convenience functions
async def generate_outline(prompt: str, max_tokens: Optional[int] = None) -> str:
    """Generate outline using the configured LLM provider"""
    return await llm_client.generate_outline(prompt, max_tokens)

async def generate_structured(prompt: str, response_format: Dict[str, Any], max_tokens: Optional[int] = None) -> Dict[str, Any]:
    """Generate structured content using the configured LLM provider"""
    return await llm_client.generate_structured(prompt, response_format, max_tokens)

async def stream_outline(prompt: str, max_tokens: Optional[int] = None) -> AsyncGenerator[str, None]:
    """Stream outline generation using the configured LLM provider"""
    async for chunk in llm_client.stream_outline(prompt, max_tokens):
        yield chunk

async def stream_structured(prompt: str, response_format: Dict[str, Any], max_tokens: Optional[int] = None) -> AsyncGenerator[str, None]:
    """Stream structured content generation using the configured LLM provider"""
    async for chunk in llm_client.stream_structured(prompt, response_format, max_tokens):
        yield chunk
