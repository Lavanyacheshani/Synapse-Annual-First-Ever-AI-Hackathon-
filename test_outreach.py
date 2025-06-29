#!/usr/bin/env python3
"""
Test script to verify outreach message generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent.outreach import OutreachGenerator

def test_outreach_generation():
    """Test outreach message generation"""
    
    print("🧪 Testing Outreach Message Generation")
    print("=" * 50)
    
    # Initialize outreach generator
    generator = OutreachGenerator()
    
    # Test candidate data
    test_candidates = [
        {
            'name': 'Jeff Andrews',
            'headline': 'Full-Stack Engineer | React, TypeScript, Java, & AWS | Financial Services | Veteran',
            'fit_score': 7.3,
            'score_breakdown': {
                'education': {'score': 5.0},
                'trajectory': {'score': 8.0},
                'company': {'score': 7.5},
                'experience': {'score': 9.5},
                'location': {'score': 6.0},
                'tenure': {'score': 6.0}
            }
        },
        {
            'name': 'William Chen',
            'headline': 'Senior Software Engineer at Google | Python, Machine Learning, Cloud',
            'fit_score': 8.5,
            'score_breakdown': {
                'education': {'score': 9.0},
                'trajectory': {'score': 9.0},
                'company': {'score': 9.5},
                'experience': {'score': 8.5},
                'location': {'score': 7.0},
                'tenure': {'score': 8.0}
            }
        }
    ]
    
    job_description = """Senior Software Engineer at Windsurf

We're looking for a talented Senior Software Engineer to join our team at Windsurf. You'll be working on cutting-edge web applications using React, TypeScript, and modern cloud technologies.

Requirements:
- 3+ years of experience with React and TypeScript
- Experience with cloud platforms (AWS, GCP, or Azure)
- Strong problem-solving skills
- Experience with modern web development practices

This is a full-time position with competitive salary and benefits."""
    
    print(f"📝 Job Description: {job_description[:100]}...")
    print()
    
    # Generate messages for each candidate
    for i, candidate in enumerate(test_candidates, 1):
        print(f"👤 Candidate {i}: {candidate['name']}")
        print(f"   Headline: {candidate['headline']}")
        print(f"   Fit Score: {candidate['fit_score']}/10")
        
        # Generate message
        message = generator._generate_fallback_message(candidate, job_description)
        
        print(f"   📧 Outreach Message:")
        print(f"   '{message}'")
        print(f"   Message Length: {len(message)} characters")
        print("-" * 50)
        print()
    
    # Test with OpenAI if available
    if generator.use_openai:
        print("🤖 Testing with OpenAI...")
        try:
            messages = generator.generate_all(test_candidates, job_description)
            for i, candidate in enumerate(messages, 1):
                print(f"🤖 OpenAI Message {i}:")
                print(f"   '{candidate['outreach_message']}'")
                print(f"   Length: {len(candidate['outreach_message'])} characters")
                print()
        except Exception as e:
            print(f"❌ OpenAI test failed: {e}")
    else:
        print("⚠️ OpenAI not available - using fallback messages only")
    
    print("✅ Outreach message generation test completed!")

if __name__ == "__main__":
    test_outreach_generation() 