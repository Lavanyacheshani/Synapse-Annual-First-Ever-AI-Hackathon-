#!/usr/bin/env python3
"""
FastAPI server for LinkedIn candidate sourcing and outreach
"""

import sys
import os
import json
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import LinkedInAgent

app = FastAPI(
    title="LinkedIn Candidate Sourcing API",
    description="AI-powered LinkedIn candidate sourcing, scoring, and outreach generation",
    version="1.0.0"
)

# Initialize the agent
agent = LinkedInAgent()

class JobRequest(BaseModel):
    job_description: str
    max_candidates: int = 10

class JobResponse(BaseModel):
    job_description: str
    timestamp: str
    total_candidates_found: int
    top_candidates: List[Dict[str, Any]]
    processing_time: float

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LinkedIn Candidate Sourcing API",
        "version": "1.0.0",
        "endpoints": {
            "POST /candidates": "Get top candidates for a job",
            "POST /batch": "Process multiple jobs",
            "GET /health": "Health check",
            "GET /stats": "System statistics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": True
    }

@app.post("/candidates", response_model=JobResponse)
async def get_candidates(request: JobRequest):
    """
    Get top candidates for a job description
    
    Returns:
    - job_description: The input job description
    - timestamp: When the request was processed
    - total_candidates_found: Total number of candidates found
    - top_candidates: List of top 10 candidates with:
        - name: Candidate name
        - linkedin_url: LinkedIn profile URL
        - headline: Professional headline
        - fit_score: Overall fit score (0-10)
        - score_breakdown: Detailed scoring breakdown
        - outreach_message: Personalized outreach message
        - key_characteristics: Key profile characteristics
        - job_matches: How profile matches the job
    - processing_time: Time taken to process
    """
    try:
        start_time = datetime.now()
        
        # Get candidates using the agent
        result = agent.process_job(
            job_description=request.job_description,
            max_candidates=request.max_candidates
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Format the response to match your exact requirements
        formatted_candidates = []
        for candidate in result['top_candidates']:
            # Extract key characteristics from the candidate profile
            key_characteristics = {
                "education": candidate.get('education', 'Not specified'),
                "experience": candidate.get('experience', 'Not specified'),
                "skills": candidate.get('skills', []),
                "company": candidate.get('company', 'Not specified'),
                "location": candidate.get('location', 'Not specified'),
                "tenure": candidate.get('tenure', 'Not specified')
            }
            
            # Create job matches based on scoring breakdown
            score_breakdown = candidate.get('score_breakdown', {})
            job_matches = {
                "education_match": f"{score_breakdown.get('education', {}).get('score', 0)}/10 - {score_breakdown.get('education', {}).get('reason', 'No education data')}",
                "experience_match": f"{score_breakdown.get('experience', {}).get('score', 0)}/10 - {score_breakdown.get('experience', {}).get('reason', 'No experience data')}",
                "skills_match": f"{score_breakdown.get('skills', {}).get('score', 0)}/10 - {score_breakdown.get('skills', {}).get('reason', 'No skills data')}",
                "company_match": f"{score_breakdown.get('company', {}).get('score', 0)}/10 - {score_breakdown.get('company', {}).get('reason', 'No company data')}",
                "location_match": f"{score_breakdown.get('location', {}).get('score', 0)}/10 - {score_breakdown.get('location', {}).get('reason', 'No location data')}",
                "tenure_match": f"{score_breakdown.get('tenure', {}).get('score', 0)}/10 - {score_breakdown.get('tenure', {}).get('reason', 'No tenure data')}"
            }
            
            formatted_candidate = {
                "name": candidate['name'],
                "linkedin_url": candidate['linkedin_url'],
                "headline": candidate['headline'],
                "fit_score": candidate['fit_score'],
                "score_breakdown": score_breakdown,
                "outreach_message": candidate['outreach_message'],
                "key_characteristics": key_characteristics,
                "job_matches": job_matches
            }
            formatted_candidates.append(formatted_candidate)
        
        return JobResponse(
            job_description=request.job_description,
            timestamp=datetime.now().isoformat(),
            total_candidates_found=result['total_candidates_found'],
            top_candidates=formatted_candidates,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing job: {str(e)}")

@app.post("/batch")
async def batch_process(jobs: List[JobRequest]):
    """Process multiple jobs in batch"""
    results = []
    for job in jobs:
        try:
            result = await get_candidates(job)
            results.append(result)
        except Exception as e:
            results.append({
                "error": str(e),
                "job_description": job.job_description
            })
    return {"results": results}

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "total_requests_processed": 0,  # Would track this in production
        "average_processing_time": 0,   # Would track this in production
        "cache_hit_rate": 0,           # Would track this in production
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 