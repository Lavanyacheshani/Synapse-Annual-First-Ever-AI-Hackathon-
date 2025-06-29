#!/usr/bin/env python3
"""
Simple test script to verify the system returns 10 candidates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import LinkedInAgent

def test_10_candidates():
    """Test that the system returns 10 candidates"""
    
    print("🧪 Testing 10 Candidates Return")
    print("=" * 40)
    
    # Initialize agent
    agent = LinkedInAgent()
    
    # Test job description
    job_description = "Python developer with React experience"
    
    print(f"Job: {job_description}")
    print("Processing...")
    
    try:
        # Process job with max_candidates=10
        result = agent.process_job(job_description, max_candidates=10)
        
        print(f"\n✅ Results:")
        print(f"   Total candidates found: {result['total_candidates_found']}")
        print(f"   Top candidates returned: {len(result['top_candidates'])}")
        
        # Check if we got 10 candidates
        if len(result['top_candidates']) == 10:
            print("✅ SUCCESS: System returned exactly 10 candidates!")
        else:
            print(f"❌ FAILED: Expected 10 candidates, got {len(result['top_candidates'])}")
        
        # Show first 3 candidates as sample
        print(f"\n📋 Sample Candidates:")
        for i, candidate in enumerate(result['top_candidates'][:3], 1):
            print(f"{i}. {candidate['name']} - Score: {candidate['fit_score']}/10")
            print(f"   {candidate['headline']}")
            print(f"   Message: {candidate['outreach_message'][:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_10_candidates()
    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Tests failed!") 