#!/bin/bash
# Curl Test Script for LinkedIn Sourcing Agent API
# Run this script to test all API functionality

BASE_URL="http://localhost:8000"

echo "🚀 Starting API Test Suite with curl"
echo "=================================================="

# Test 1: Health Check
echo -e "\n🔍 Testing Health Check..."
response=$(curl -s -w "%{http_code}" "$BASE_URL/health")
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" -eq 200 ]; then
    echo "✅ Health Check PASSED"
    echo "   Response: $body"
else
    echo "❌ Health Check FAILED: HTTP $http_code"
fi

# Test 2: Root Endpoint
echo -e "\n🔍 Testing Root Endpoint..."
response=$(curl -s -w "%{http_code}" "$BASE_URL/")
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" -eq 200 ]; then
    echo "✅ Root Endpoint PASSED"
    echo "   Response: $body"
else
    echo "❌ Root Endpoint FAILED: HTTP $http_code"
fi

# Test 3: Stats Endpoint
echo -e "\n🔍 Testing Stats Endpoint..."
response=$(curl -s -w "%{http_code}" "$BASE_URL/stats")
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" -eq 200 ]; then
    echo "✅ Stats Endpoint PASSED"
    echo "   Response: $body"
else
    echo "❌ Stats Endpoint FAILED: HTTP $http_code"
fi

# Test 4: Single Job Candidates (Main Functionality)
echo -e "\n🔍 Testing Single Job Candidates..."
job_description='{
  "job_description": "Software Engineer, ML Research at Windsurf (Codeium) - We are recruiting for a Software Engineer, ML Research role at Windsurf (the company behind Codeium) - a Forbes AI 50 company building AI-powered developer tools. They are looking for someone to train LLMs for code generation, with $140-300k + equity in Mountain View.",
  "max_candidates": 10,
  "enable_multi_source": true,
  "include_score_breakdown": true
}'

response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/candidates" \
  -H "Content-Type: application/json" \
  -d "$job_description")
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" -eq 200 ]; then
    echo "✅ Single Job Candidates PASSED"
    echo "   Response: $body"
else
    echo "❌ Single Job Candidates FAILED: HTTP $http_code"
    echo "   Response: $body"
fi

# Test 5: Batch Jobs
echo -e "\n🔍 Testing Batch Jobs..."
batch_payload='{
  "job_descriptions": [
    "Senior Backend Engineer at fintech startup in San Francisco",
    "Frontend Developer with React experience in New York",
    "Data Scientist with Python and ML experience in Austin"
  ],
  "max_candidates_per_job": 5,
  "enable_multi_source": true
}'

response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/batch" \
  -H "Content-Type: application/json" \
  -d "$batch_payload")
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" -eq 200 ]; then
    echo "✅ Batch Jobs PASSED"
    echo "   Response: $body"
else
    echo "❌ Batch Jobs FAILED: HTTP $http_code"
    echo "   Response: $body"
fi

# Test 6: Cache Operations
echo -e "\n🔍 Testing Cache Operations..."
response=$(curl -s -w "%{http_code}" -X DELETE "$BASE_URL/cache/expired")
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" -eq 200 ]; then
    echo "✅ Clear Expired Cache PASSED"
    echo "   Response: $body"
else
    echo "❌ Clear Expired Cache FAILED: HTTP $http_code"
fi

# Test 7: Error Handling
echo -e "\n🔍 Testing Error Handling..."

# Test empty job description
response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/candidates" \
  -H "Content-Type: application/json" \
  -d '{"job_description": ""}')
http_code="${response: -3}"

if [ "$http_code" -eq 400 ]; then
    echo "✅ Empty Job Description Error Handling PASSED"
else
    echo "❌ Empty Job Description Error Handling FAILED: HTTP $http_code"
fi

# Test invalid endpoint
response=$(curl -s -w "%{http_code}" "$BASE_URL/invalid")
http_code="${response: -3}"

if [ "$http_code" -eq 404 ]; then
    echo "✅ Invalid Endpoint Error Handling PASSED"
else
    echo "❌ Invalid Endpoint Error Handling FAILED: HTTP $http_code"
fi

echo -e "\n=================================================="
echo "🎉 API Test Suite Complete!"
echo "Check the results above to see which tests passed." 