# PowerShell Test Script for LinkedIn Sourcing Agent API
# Run this script to test all API functionality

$BaseUrl = "http://localhost:8000"
$Headers = @{
    "Content-Type" = "application/json"
}

Write-Host "🚀 Starting API Test Suite" -ForegroundColor Green
Write-Host "=" * 50

# Test 1: Health Check
Write-Host "`n🔍 Testing Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get
    Write-Host "✅ Health Check PASSED" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   API Keys Valid: $($response.api_keys_valid)" -ForegroundColor White
} catch {
    Write-Host "❌ Health Check FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Root Endpoint
Write-Host "`n🔍 Testing Root Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/" -Method Get
    Write-Host "✅ Root Endpoint PASSED" -ForegroundColor Green
    Write-Host "   Message: $($response.message)" -ForegroundColor White
    Write-Host "   Version: $($response.version)" -ForegroundColor White
} catch {
    Write-Host "❌ Root Endpoint FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Stats Endpoint
Write-Host "`n🔍 Testing Stats Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/stats" -Method Get
    Write-Host "✅ Stats Endpoint PASSED" -ForegroundColor Green
    Write-Host "   Cache Stats: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor White
} catch {
    Write-Host "❌ Stats Endpoint FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Single Job Candidates (Main Functionality)
Write-Host "`n🔍 Testing Single Job Candidates..." -ForegroundColor Yellow
$jobDescription = @"
Software Engineer, ML Research at Windsurf (Codeium)

We're recruiting for a Software Engineer, ML Research role at Windsurf (the company behind Codeium) - a Forbes AI 50 company building AI-powered developer tools. They're looking for someone to train LLMs for code generation, with `$140-300k + equity in Mountain View.

Requirements:
- Experience with machine learning and LLM training
- Strong programming skills in Python
- Experience with code generation or developer tools
- Located in Mountain View or willing to relocate
"@

$payload = @{
    job_description = $jobDescription
    max_candidates = 10
    enable_multi_source = $true
    include_score_breakdown = $true
} | ConvertTo-Json -Depth 3

try {
    Write-Host "   Sending request..." -ForegroundColor White
    $response = Invoke-RestMethod -Uri "$BaseUrl/candidates" -Method Post -Body $payload -Headers $Headers
    Write-Host "✅ Single Job Candidates PASSED" -ForegroundColor Green
    Write-Host "   Job ID: $($response.job_id)" -ForegroundColor White
    Write-Host "   Candidates Found: $($response.candidates_found)" -ForegroundColor White
    Write-Host "   Candidates Scored: $($response.candidates_scored)" -ForegroundColor White
    Write-Host "   Outreach Generated: $($response.outreach_generated)" -ForegroundColor White
    Write-Host "   Processing Time: $($response.processing_time)s" -ForegroundColor White
    Write-Host "   Top Candidates: $($response.top_candidates.Count)" -ForegroundColor White
    
    if ($response.top_candidates.Count -gt 0) {
        $firstCandidate = $response.top_candidates[0]
        Write-Host "`n   📋 First Candidate Details:" -ForegroundColor Cyan
        Write-Host "      Name: $($firstCandidate.name)" -ForegroundColor White
        Write-Host "      LinkedIn: $($firstCandidate.linkedin_url)" -ForegroundColor White
        Write-Host "      Fit Score: $($firstCandidate.fit_score)" -ForegroundColor White
        Write-Host "      Confidence: $($firstCandidate.overall_confidence)" -ForegroundColor White
        if ($firstCandidate.score_breakdown) {
            Write-Host "      Score Breakdown: $($firstCandidate.score_breakdown | ConvertTo-Json)" -ForegroundColor White
        }
        Write-Host "      Outreach Message: $($firstCandidate.outreach_message.Substring(0, [Math]::Min(100, $firstCandidate.outreach_message.Length)))..." -ForegroundColor White
    }
} catch {
    Write-Host "❌ Single Job Candidates FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
}

# Test 5: Batch Jobs
Write-Host "`n🔍 Testing Batch Jobs..." -ForegroundColor Yellow
$batchPayload = @{
    job_descriptions = @(
        "Senior Backend Engineer at fintech startup in San Francisco",
        "Frontend Developer with React experience in New York",
        "Data Scientist with Python and ML experience in Austin"
    )
    max_candidates_per_job = 5
    enable_multi_source = $true
} | ConvertTo-Json -Depth 3

try {
    Write-Host "   Sending batch request..." -ForegroundColor White
    $response = Invoke-RestMethod -Uri "$BaseUrl/batch" -Method Post -Body $batchPayload -Headers $Headers
    Write-Host "✅ Batch Jobs PASSED" -ForegroundColor Green
    Write-Host "   Batch ID: $($response.batch_id)" -ForegroundColor White
    Write-Host "   Total Jobs: $($response.total_jobs)" -ForegroundColor White
    Write-Host "   Total Candidates: $($response.total_candidates)" -ForegroundColor White
    Write-Host "   Processing Time: $($response.processing_time)s" -ForegroundColor White
    Write-Host "   Results: $($response.results.Count)" -ForegroundColor White
    
    for ($i = 0; $i -lt $response.results.Count; $i++) {
        $result = $response.results[$i]
        Write-Host "`n   📋 Job $($i+1) Results:" -ForegroundColor Cyan
        Write-Host "      Description: $($result.job_description.Substring(0, [Math]::Min(50, $result.job_description.Length)))..." -ForegroundColor White
        Write-Host "      Candidates Found: $($result.candidates_found)" -ForegroundColor White
        Write-Host "      Top Candidates: $($result.top_candidates.Count)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Batch Jobs FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Cache Operations
Write-Host "`n🔍 Testing Cache Operations..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/cache/expired" -Method Delete
    Write-Host "✅ Clear Expired Cache PASSED" -ForegroundColor Green
    Write-Host "   Cleared Items: $($response.cleared_count)" -ForegroundColor White
} catch {
    Write-Host "❌ Clear Expired Cache FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Error Handling
Write-Host "`n🔍 Testing Error Handling..." -ForegroundColor Yellow
try {
    $emptyPayload = @{ job_description = "" } | ConvertTo-Json
    Invoke-RestMethod -Uri "$BaseUrl/candidates" -Method Post -Body $emptyPayload -Headers $Headers
    Write-Host "❌ Empty Job Description Error Handling FAILED: Should have returned 400" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✅ Empty Job Description Error Handling PASSED" -ForegroundColor Green
    } else {
        Write-Host "❌ Empty Job Description Error Handling FAILED: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

try {
    Invoke-RestMethod -Uri "$BaseUrl/invalid" -Method Get
    Write-Host "❌ Invalid Endpoint Error Handling FAILED: Should have returned 404" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "✅ Invalid Endpoint Error Handling PASSED" -ForegroundColor Green
    } else {
        Write-Host "❌ Invalid Endpoint Error Handling FAILED: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

Write-Host "`n" + "=" * 50
Write-Host "🎉 API Test Suite Complete!" -ForegroundColor Green
Write-Host "Check the results above to see which tests passed." -ForegroundColor White 