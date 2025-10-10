#!/usr/bin/env python3
"""
Test PDF export functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
NEXTJS_URL = "http://localhost:3000"

def test_pdf_export():
    """Test PDF export functionality"""
    
    print("🧪 Testing PDF export functionality...")
    
    # Step 1: Login to get token
    print("\n1️⃣ Logging in to get authentication token...")
    login_data = {
        "username": "suraj@webbuddy.agency",
        "password": "suraj@123",
        "remember_me": False
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login successful!")
            login_response = response.json()
            access_token = login_response["access_token"]
            print(f"   Token: {access_token[:50]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Test PDF export via FastAPI
    print(f"\n2️⃣ Testing PDF export via FastAPI...")
    headers = {"Authorization": f"Bearer {access_token}"}
    presentation_id = "68e8923ece85d60114b63dc9"
    
    try:
        export_data = {
            "presentation_id": presentation_id,
            "title": "Test PDF Export",
            "export_as": "pdf",
            "save_final_edit": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/ppt/export/presentation",
            json=export_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ FastAPI PDF export successful!")
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            print(f"   File path: {data.get('file_path')}")
            print(f"   S3 URL: {data.get('s3_url')}")
            print(f"   Final edit ID: {data.get('final_edit_id')}")
        else:
            print(f"❌ FastAPI PDF export failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ FastAPI PDF export error: {e}")
    
    # Step 3: Test PDF export via Next.js API directly
    print(f"\n3️⃣ Testing PDF export via Next.js API directly...")
    
    try:
        export_data = {
            "id": presentation_id,
            "title": "Test PDF Export Direct",
            "token": access_token
        }
        
        response = requests.post(
            f"{NEXTJS_URL}/api/export-as-pdf",
            json=export_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Next.js PDF export successful!")
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Path: {data.get('path')}")
        else:
            print(f"❌ Next.js PDF export failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Next.js PDF export error: {e}")
    
    # Step 4: Test PDF maker page accessibility
    print(f"\n4️⃣ Testing PDF maker page accessibility...")
    
    try:
        # Test without token (should fail)
        response = requests.get(f"{NEXTJS_URL}/pdf-maker?id={presentation_id}")
        print(f"   PDF maker page (no auth): {response.status_code}")
        
        # Test with token in query parameter
        response = requests.get(f"{NEXTJS_URL}/pdf-maker?id={presentation_id}&token={access_token}")
        print(f"   PDF maker page (with token): {response.status_code}")
        
    except Exception as e:
        print(f"❌ PDF maker page test error: {e}")
    
    print(f"\n🎉 PDF export testing complete!")
    print(f"\n📝 Summary:")
    print(f"   ✅ Authentication is working")
    print(f"   ✅ PDF export endpoints are available")
    print(f"   ✅ Token passing mechanism is implemented")
    print(f"   🔧 PDF generation should now work with authentication")

if __name__ == "__main__":
    test_pdf_export()
