# PowerShell Demo Script for LinkedIn Sourcing Agent
# Run this to test with your own job description

$BaseUrl = "http://localhost:8000"
$Headers = @{
    "Content-Type" = "application/json"
}

Write-Host "🚀 LinkedIn Sourcing Agent Demo" -ForegroundColor Green
Write-Host "=" * 50

Write-Host "`n📝 Enter your job description:" -ForegroundColor Yellow
Write-Host "(Type your job description and press Enter when done)" -ForegroundColor White

$jobDescription = Read-Host "Job Description"

if ([string]::IsNullOrWhiteSpace($jobDescription)) {
    Write-Host "❌ Job description cannot be empty!" -ForegroundColor Red
    exit
}

Write-Host "`n✅ Job Description Received:" -ForegroundColor Green
Write-Host "'$($jobDescription.Substring(0, [Math]::Min(100, $jobDescription.Length)))...'" -ForegroundColor White

$payload = @{
    job_description = $jobDescription
    max_candidates = 10
    enable_multi_source = $true
    include_score_breakdown = $true
} | ConvertTo-Json -Depth 3

Write-Host "`n🔍 Searching for candidates..." -ForegroundColor Yellow
Write-Host "(This may take 20-30 seconds)" -ForegroundColor White

try {
    $startTime = Get-Date
    $response = Invoke-RestMethod -Uri "$BaseUrl/candidates" -Method Post -Body $payload -Headers $Headers
    $processingTime = (Get-Date) - $startTime
    
    Write-Host "`n🎉 SUCCESS! Found $($response.candidates_found) candidates" -ForegroundColor Green
    Write-Host "⏱️  Processing time: $($response.processing_time)s" -ForegroundColor White
    Write-Host "📊 Candidates scored: $($response.candidates_scored)" -ForegroundColor White
    Write-Host "💬 Outreach messages generated: $($response.outreach_generated)" -ForegroundColor White
    
    Write-Host "`n🏆 TOP CANDIDATES:" -ForegroundColor Cyan
    Write-Host "=" * 50
    
    for ($i = 0; $i -lt [Math]::Min(5, $response.top_candidates.Count); $i++) {
        $candidate = $response.top_candidates[$i]
        
        Write-Host "`n$($i + 1). $($candidate.name)" -ForegroundColor Yellow
        Write-Host "   LinkedIn: $($candidate.linkedin_url)" -ForegroundColor White
        Write-Host "   Headline: $($candidate.headline)" -ForegroundColor White
        Write-Host "   Fit Score: $($candidate.fit_score)/10" -ForegroundColor Green
        Write-Host "   Confidence: $([Math]::Round($candidate.overall_confidence, 2))" -ForegroundColor White
        
        if ($candidate.score_breakdown) {
            Write-Host "   Score Breakdown:" -ForegroundColor Cyan
            foreach ($category in $candidate.score_breakdown.Keys) {
                $details = $candidate.score_breakdown[$category]
                if ($details -and $details.score) {
                    Write-Host "     - $($category.ToUpper()): $($details.score)/10" -ForegroundColor White
                }
            }
        }
        
        Write-Host "   Outreach Message:" -ForegroundColor Cyan
        Write-Host "     '$($candidate.outreach_message.Substring(0, [Math]::Min(150, $candidate.outreach_message.Length)))...'" -ForegroundColor White
        Write-Host "-" * 30
    }
    
    Write-Host "`n📋 API Response Summary:" -ForegroundColor Cyan
    Write-Host "   Job ID: $($response.job_id)" -ForegroundColor White
    Write-Host "   Total candidates found: $($response.candidates_found)" -ForegroundColor White
    Write-Host "   Processing time: $($response.processing_time)s" -ForegroundColor White
    
    # Save results to file
    $timestamp = [DateTimeOffset]::Now.ToUnixTimeSeconds()
    $filename = "job_results_$timestamp.json"
    $response | ConvertTo-Json -Depth 10 | Out-File -FilePath $filename -Encoding UTF8
    Write-Host "`n💾 Results saved to: $filename" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody" -ForegroundColor Red
    }
}

Write-Host "`n" + "=" * 50
Write-Host "🎉 Demo Complete!" -ForegroundColor Green 