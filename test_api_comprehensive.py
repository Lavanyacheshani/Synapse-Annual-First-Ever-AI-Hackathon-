#!/usr/bin/env python3
"""
Comprehensive API Test Script for LinkedIn Sourcing Agent
Tests all endpoints and functionality
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_health_check():
    """Test the health endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check PASSED")
            print(f"   Status: {data['status']}")
            print(f"   API Keys Valid: {data['api_keys_valid']}")
            return True
        else:
            print(f"❌ Health Check FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check ERROR: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🔍 Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root Endpoint PASSED")
            print(f"   Message: {data['message']}")
            print(f"   Version: {data['version']}")
            print(f"   Available Endpoints: {len(data['endpoints'])}")
            return True
        else:
            print(f"❌ Root Endpoint FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root Endpoint ERROR: {e}")
        return False

def test_stats_endpoint():
    """Test the stats endpoint"""
    print("\n🔍 Testing Stats Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats Endpoint PASSED")
            print(f"   Cache Stats: {data}")
            return True
        else:
            print(f"❌ Stats Endpoint FAILED: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats Endpoint ERROR: {e}")
        return False

def test_single_job_candidates():
    """Test the main candidates endpoint with a single job"""
    print("\n🔍 Testing Single Job Candidates...")
    
    # Test job description from the challenge
    job_description = """Software Engineer, ML Research at Windsurf (Codeium)
    
    We're recruiting for a Software Engineer, ML Research role at Windsurf (the company behind Codeium) - a Forbes AI 50 company building AI-powered developer tools. They're looking for someone to train LLMs for code generation, with $140-300k + equity in Mountain View.
    
    Requirements:
    - Experience with machine learning and LLM training
    - Strong programming skills in Python
    - Experience with code generation or developer tools
    - Located in Mountain View or willing to relocate
    """
    
    payload = {
        "job_description": job_description,
        "max_candidates": 10,
        "enable_multi_source": True,
        "include_score_breakdown": True
    }
    
    try:
        print("   Sending request...")
        response = requests.post(f"{BASE_URL}/candidates", json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Single Job Candidates PASSED")
            print(f"   Job ID: {data['job_id']}")
            print(f"   Candidates Found: {data['candidates_found']}")
            print(f"   Candidates Scored: {data['candidates_scored']}")
            print(f"   Outreach Generated: {data['outreach_generated']}")
            print(f"   Processing Time: {data['processing_time']}s")
            print(f"   Top Candidates: {len(data['top_candidates'])}")
            
            # Show details of first candidate
            if data['top_candidates']:
                first_candidate = data['top_candidates'][0]
                print(f"\n   📋 First Candidate Details:")
                print(f"      Name: {first_candidate['name']}")
                print(f"      LinkedIn: {first_candidate['linkedin_url']}")
                print(f"      Fit Score: {first_candidate['fit_score']}")
                print(f"      Confidence: {first_candidate['overall_confidence']}")
                if 'score_breakdown' in first_candidate:
                    print(f"      Score Breakdown: {first_candidate['score_breakdown']}")
                print(f"      Outreach Message: {first_candidate['outreach_message'][:100]}...")
            
            return True
        else:
            print(f"❌ Single Job Candidates FAILED: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Single Job Candidates ERROR: {e}")
        return False

def test_batch_jobs():
    """Test batch processing with multiple jobs"""
    print("\n🔍 Testing Batch Jobs...")
    
    job_descriptions = [
        "Senior Backend Engineer at fintech startup in San Francisco",
        "Frontend Developer with React experience in New York",
        "Data Scientist with Python and ML experience in Austin"
    ]
    
    payload = {
        "job_descriptions": job_descriptions,
        "max_candidates_per_job": 5,
        "enable_multi_source": True
    }
    
    try:
        print("   Sending batch request...")
        response = requests.post(f"{BASE_URL}/batch", json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch Jobs PASSED")
            print(f"   Batch ID: {data['batch_id']}")
            print(f"   Total Jobs: {data['total_jobs']}")
            print(f"   Total Candidates: {data['total_candidates']}")
            print(f"   Processing Time: {data['processing_time']}s")
            print(f"   Results: {len(data['results'])}")
            
            # Show summary of each job result
            for i, result in enumerate(data['results']):
                print(f"\n   📋 Job {i+1} Results:")
                print(f"      Description: {result['job_description'][:50]}...")
                print(f"      Candidates Found: {result['candidates_found']}")
                print(f"      Top Candidates: {len(result['top_candidates'])}")
            
            return True
        else:
            print(f"❌ Batch Jobs FAILED: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Batch Jobs ERROR: {e}")
        return False

def test_cache_operations():
    """Test cache operations"""
    print("\n🔍 Testing Cache Operations...")
    
    try:
        # Test clear expired cache
        response = requests.delete(f"{BASE_URL}/cache/expired")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Clear Expired Cache PASSED")
            print(f"   Cleared Items: {data['cleared_count']}")
        else:
            print(f"❌ Clear Expired Cache FAILED: {response.status_code}")
        
        # Test get stats again to see cache state
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   Updated Cache Stats: {data}")
        
        return True
    except Exception as e:
        print(f"❌ Cache Operations ERROR: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n🔍 Testing Error Handling...")
    
    # Test with empty job description
    payload = {"job_description": ""}
    try:
        response = requests.post(f"{BASE_URL}/candidates", json=payload, headers=HEADERS)
        if response.status_code == 400:
            print(f"✅ Empty Job Description Error Handling PASSED")
        else:
            print(f"❌ Empty Job Description Error Handling FAILED: {response.status_code}")
    except Exception as e:
        print(f"❌ Empty Job Description Error Handling ERROR: {e}")
    
    # Test with invalid endpoint
    try:
        response = requests.get(f"{BASE_URL}/invalid")
        if response.status_code == 404:
            print(f"✅ Invalid Endpoint Error Handling PASSED")
        else:
            print(f"❌ Invalid Endpoint Error Handling FAILED: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid Endpoint Error Handling ERROR: {e}")
    
    return True

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Comprehensive API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Stats Endpoint", test_stats_endpoint),
        ("Single Job Candidates", test_single_job_candidates),
        ("Batch Jobs", test_batch_jobs),
        ("Cache Operations", test_cache_operations),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your API is working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("⏳ Waiting 2 seconds for server to be ready...")
    time.sleep(2)
    
    success = run_comprehensive_test()
    exit(0 if success else 1) 