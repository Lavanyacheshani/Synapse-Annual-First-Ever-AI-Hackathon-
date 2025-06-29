#!/usr/bin/env python3
"""
Test script for Hugging Face Spaces deployment
"""

import requests
import json
import time

def test_hf_space():
    """Test the deployed Hugging Face Space"""
    
    # Replace with your actual Hugging Face Space URL
    base_url = "https://lavanyacheshani-ai-hack-api.hf.space"
    
    print("🧪 Testing Hugging Face Space Deployment")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print()
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print()
    
    # Test 2: Root endpoint
    print("2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data['message']}")
            print(f"   Agent ready: {data.get('agent_ready', 'Unknown')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    print()
    
    # Test 3: Candidates endpoint
    print("3. Testing candidates endpoint...")
    job_description = """
    Senior Software Engineer - Full Stack Development
    
    We are looking for a Senior Software Engineer with expertise in:
    - React, TypeScript, and modern JavaScript frameworks
    - Python backend development (FastAPI, Django)
    - AWS cloud services and infrastructure
    - Database design and optimization (PostgreSQL, MongoDB)
    
    Requirements:
    - 5+ years of software development experience
    - Bachelor's degree in Computer Science or related field
    - Experience with microservices architecture
    - Strong problem-solving and communication skills
    
    Location: Remote or San Francisco, CA
    """
    
    payload = {
        "job_description": job_description,
        "max_candidates": 5
    }
    
    try:
        print("   Sending job request...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/candidates",
            json=payload,
            timeout=120  # Longer timeout for processing
        )
        
        request_time = time.time() - start_time
        print(f"   Request completed in {request_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Candidates endpoint successful!")
            print(f"   Total candidates found: {data['total_candidates_found']}")
            print(f"   Processing time: {data['processing_time']:.2f}s")
            print(f"   Top candidates returned: {len(data['top_candidates'])}")
            
            # Show first candidate details
            if data['top_candidates']:
                first_candidate = data['top_candidates'][0]
                print(f"   First candidate: {first_candidate['name']} (Score: {first_candidate['fit_score']}/10)")
                print(f"   Outreach message preview: {first_candidate['outreach_message'][:100]}...")
            
        elif response.status_code == 503:
            print("⚠️  Agent not ready - this is normal during initial deployment")
            print(f"   Response: {response.text}")
        else:
            print(f"❌ Candidates endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - this might be normal during initial deployment")
    except Exception as e:
        print(f"❌ Candidates endpoint error: {e}")
    
    print()
    
    # Test 4: Stats endpoint
    print("4. Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/stats", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint: {data}")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
    
    print()
    print("🎉 Testing completed!")
    print("=" * 60)
    print("📝 Next steps:")
    print("1. Check the logs in your Hugging Face Space for any errors")
    print("2. Set up environment variables (GOOGLE_API_KEY, GOOGLE_CSE_ID, etc.)")
    print("3. Test with different job descriptions")
    print("4. Share your API link: " + base_url)

if __name__ == "__main__":
    test_hf_space() 