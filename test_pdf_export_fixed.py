#!/usr/bin/env python3
"""
Test script to validate the fixed PDF export functionality.
This script tests both the original and new canvas-based PDF export.
"""

import asyncio
import aiohttp
import json
import os
import sys
from pathlib import Path

# Add the FastAPI server path to sys.path
fastapi_path = Path(__file__).parent / "servers" / "fastapi"
sys.path.insert(0, str(fastapi_path))

async def test_pdf_export():
    """Test the PDF export functionality"""
    
    # Test configuration
    base_url = "http://localhost:8000"
    nextjs_url = "http://localhost:3000"
    
    # You'll need to replace these with actual values from your system
    test_presentation_id = "your_presentation_id_here"  # Replace with actual ID
    test_title = "Test Export - Fixed PDF"
    
    print("🧪 Testing PDF Export Functionality")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test 1: Test the new canvas-based PDF export endpoint directly
            print("\n1️⃣ Testing Canvas-based PDF Export (Next.js API)")
            print("-" * 40)
            
            canvas_export_url = f"{nextjs_url}/api/export-as-pdf-canvas"
            canvas_payload = {
                "id": test_presentation_id,
                "title": f"{test_title} - Canvas",
                "token": None  # You may need to provide a valid token
            }
            
            async with session.post(canvas_export_url, json=canvas_payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Canvas export successful: {result.get('path', 'No path returned')}")
                else:
                    error_text = await response.text()
                    print(f"❌ Canvas export failed: {response.status} - {error_text}")
            
            # Test 2: Test the original PDF export endpoint
            print("\n2️⃣ Testing Original PDF Export (Next.js API)")
            print("-" * 40)
            
            original_export_url = f"{nextjs_url}/api/export-as-pdf"
            original_payload = {
                "id": test_presentation_id,
                "title": f"{test_title} - Original",
                "token": None
            }
            
            async with session.post(original_export_url, json=original_payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Original export successful: {result.get('path', 'No path returned')}")
                else:
                    error_text = await response.text()
                    print(f"❌ Original export failed: {response.status} - {error_text}")
            
            # Test 3: Test the FastAPI export endpoint
            print("\n3️⃣ Testing FastAPI Export Endpoint")
            print("-" * 40)
            
            fastapi_export_url = f"{base_url}/api/v1/ppt/export/presentation"
            fastapi_payload = {
                "presentation_id": test_presentation_id,
                "title": f"{test_title} - FastAPI",
                "export_as": "pdf",
                "save_final_edit": True
            }
            
            # Note: This will require authentication headers
            headers = {
                "Authorization": "Bearer your_token_here",  # Replace with actual token
                "Content-Type": "application/json"
            }
            
            async with session.post(fastapi_export_url, json=fastapi_payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ FastAPI export successful: {result.get('file_path', 'No path returned')}")
                else:
                    error_text = await response.text()
                    print(f"❌ FastAPI export failed: {response.status} - {error_text}")
            
            # Test 4: Check if exported files exist
            print("\n4️⃣ Checking Exported Files")
            print("-" * 40)
            
            exports_dir = Path(__file__).parent / "app_data" / "exports"
            if exports_dir.exists():
                pdf_files = list(exports_dir.glob("*.pdf"))
                print(f"📁 Found {len(pdf_files)} PDF files in exports directory:")
                for pdf_file in pdf_files:
                    file_size = pdf_file.stat().st_size
                    print(f"   - {pdf_file.name} ({file_size:,} bytes)")
            else:
                print("❌ Exports directory not found")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

async def test_presentation_data():
    """Test if we can fetch presentation data"""
    
    print("\n5️⃣ Testing Presentation Data Fetch")
    print("-" * 40)
    
    # You'll need to replace this with actual values
    test_presentation_id = "your_presentation_id_here"
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test fetching presentation data
            url = f"{base_url}/api/v1/ppt/presentation/{test_presentation_id}"
            headers = {
                "Authorization": "Bearer your_token_here",  # Replace with actual token
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Presentation data fetched successfully")
                    print(f"   - Title: {data.get('title', 'No title')}")
                    print(f"   - Slides: {len(data.get('slides', []))}")
                    
                    # Check slide content structure
                    slides = data.get('slides', [])
                    if slides:
                        first_slide = slides[0]
                        print(f"   - First slide layout: {first_slide.get('layout', 'No layout')}")
                        print(f"   - First slide has content: {bool(first_slide.get('content'))}")
                        print(f"   - Content type: {type(first_slide.get('content'))}")
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to fetch presentation data: {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Presentation data test failed: {e}")

def print_instructions():
    """Print instructions for running the test"""
    
    print("\n📋 Test Instructions")
    print("=" * 50)
    print("Before running this test, please:")
    print("1. Replace 'your_presentation_id_here' with an actual presentation ID")
    print("2. Replace 'your_token_here' with a valid authentication token")
    print("3. Ensure both FastAPI (port 8000) and Next.js (port 3000) servers are running")
    print("4. Make sure you have a presentation with actual content to test with")
    print("\nTo get a presentation ID, you can:")
    print("- Check your database for existing presentations")
    print("- Create a new presentation through the UI")
    print("- Use the dashboard API to list presentations")
    print("\nTo get an authentication token:")
    print("- Log in through the UI and check browser dev tools")
    print("- Use the login API endpoint")

async def main():
    """Main test function"""
    
    print_instructions()
    
    # Check if we have the required configuration
    if "your_presentation_id_here" in str(Path(__file__).read_text()):
        print("\n⚠️  Please update the test script with actual values before running!")
        return
    
    await test_presentation_data()
    await test_pdf_export()
    
    print("\n🎉 Test completed!")
    print("Check the exported PDF files to verify they contain the actual slide content.")

if __name__ == "__main__":
    asyncio.run(main())
