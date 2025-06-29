#!/usr/bin/env python3
"""
Simple test script for the LinkedIn Candidate Sourcing API
Tests the exact requirements: job description input -> top 10 candidates with personalized outreach
"""

import requests
import json
import time

def test_api():
    """Test the API with a sample job description"""
    
    # API endpoint
    url = "http://localhost:8000/candidates"
    
    # Sample job description
    job_description = """
    Senior Software Engineer - Full Stack Development
    
    We are looking for a Senior Software Engineer with expertise in:
    - React, TypeScript, and modern JavaScript frameworks
    - Python backend development (FastAPI, Django)
    - AWS cloud services and infrastructure
    - Database design and optimization (PostgreSQL, MongoDB)
    - CI/CD pipelines and DevOps practices
    
    Requirements:
    - 5+ years of software development experience
    - Bachelor's degree in Computer Science or related field
    - Experience with microservices architecture
    - Strong problem-solving and communication skills
    - Experience with agile development methodologies
    
    Location: Remote or San Francisco, CA
    """
    
    # Request payload
    payload = {
        "job_description": job_description,
        "max_candidates": 10
    }
    
    print("🚀 Testing LinkedIn Candidate Sourcing API")
    print("=" * 60)
    print(f"Job Description: {job_description[:100]}...")
    print(f"Max Candidates: {payload['max_candidates']}")
    print()
    
    try:
        # Make the API request
        print("📡 Making API request...")
        start_time = time.time()
        
        response = requests.post(url, json=payload, timeout=120)
        
        request_time = time.time() - start_time
        print(f"⏱️  Request completed in {request_time:.2f} seconds")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API Response Success!")
            print("=" * 60)
            print(f"📊 Total candidates found: {data['total_candidates_found']}")
            print(f"⏰ Processing time: {data['processing_time']:.2f} seconds")
            print(f"🕐 Timestamp: {data['timestamp']}")
            print()
            
            # Display top candidates
            print("👥 TOP CANDIDATES:")
            print("=" * 60)
            
            for i, candidate in enumerate(data['top_candidates'], 1):
                print(f"\n{i}. {candidate['name']}")
                print(f"   📍 {candidate['headline']}")
                print(f"   🎯 Fit Score: {candidate['fit_score']}/10")
                print(f"   🔗 LinkedIn: {candidate['linkedin_url']}")
                
                # Key characteristics
                print(f"   📋 Key Characteristics:")
                for key, value in candidate['key_characteristics'].items():
                    if value and value != 'Not specified':
                        print(f"      • {key.title()}: {value}")
                
                # Job matches
                print(f"   🎯 Job Matches:")
                for key, value in candidate['job_matches'].items():
                    if '0/10' not in value:  # Only show non-zero matches
                        print(f"      • {key.replace('_', ' ').title()}: {value}")
                
                # Outreach message
                print(f"   💬 Outreach Message:")
                print(f"      {candidate['outreach_message']}")
                print("-" * 60)
            
            # Save response to file
            with open('api_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Full response saved to 'api_response.json'")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Error details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the API server is running on http://localhost:8000")
        print("   Run: cd api && python -m uvicorn main:app --host 0.0.0.0 --port 8000")
        
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long to complete")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")

if __name__ == "__main__":
    test_api() 