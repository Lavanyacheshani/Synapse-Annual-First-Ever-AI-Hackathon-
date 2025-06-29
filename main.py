#!/usr/bin/env python3
"""
Main FastAPI application for LinkedIn candidate sourcing
"""

import sys
import os
import json
from typing import List, Dict, Any
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import our agent modules
try:
    from agent import LinkedInAgent
    agent = LinkedInAgent()
    AGENT_READY = True
except Exception as e:
    print(f"Warning: Could not initialize agent: {e}")
    AGENT_READY = False

app = FastAPI(
    title="LinkedIn Candidate Sourcing API",
    description="AI-powered LinkedIn candidate sourcing, scoring, and outreach generation",
    version="1.0.0"
)

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
        "status": "running",
        "endpoints": {
            "POST /candidates": "Get top candidates for a job",
            "GET /health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_ready": AGENT_READY
    }

@app.post("/candidates", response_model=JobResponse)
async def get_candidates(request: JobRequest):
    """
    Get top candidates for a job description
    
    Returns:
    - job_description: The input job description
    - timestamp: When the request was processed
    - total_candidates_found: Total number of candidates found
    - top_candidates: List of top candidates with:
        - name: Candidate name
        - linkedin_url: LinkedIn profile URL
        - headline: Professional headline
        - fit_score: Overall fit score (0-10)
        - score_breakdown: Detailed scoring breakdown
        - outreach_message: Personalized outreach message
    - processing_time: Time taken to process
    """
    if not AGENT_READY:
        raise HTTPException(status_code=500, detail="Agent not ready")
    
    try:
        start_time = datetime.now()
        
        # Get candidates using the agent
        result = agent.process_job(
            job_description=request.job_description,
            max_candidates=request.max_candidates
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Format the response
        formatted_candidates = []
        for candidate in result['top_candidates']:
            formatted_candidate = {
                "name": candidate['name'],
                "linkedin_url": candidate['linkedin_url'],
                "headline": candidate['headline'],
                "fit_score": candidate['fit_score'],
                "score_breakdown": candidate.get('score_breakdown', {}),
                "outreach_message": candidate['outreach_message']
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 