#!/usr/bin/env python3
"""
Demo Script for LinkedIn Sourcing Agent
Enter your own job description and see the results!
"""

import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def demo_with_custom_job():
    """Demo the API with a custom job description"""
    
    print("🚀 LinkedIn Sourcing Agent Demo")
    print("=" * 50)
    
    # Get custom job description from user
    print("\n📝 Enter your job description:")
    print("(Press Enter twice when done)")
    
    lines = []
    while True:
        line = input()
        if line == "" and lines:  # Empty line and we have content
            break
        if line == "" and not lines:  # First empty line, continue
            continue
        lines.append(line)
    
    job_description = "\n".join(lines)
    
    if not job_description.strip():
        print("❌ Job description cannot be empty!")
        return
    
    print(f"\n✅ Job Description Received:")
    print(f"'{job_description[:100]}...'")
    
    # Prepare the request
    payload = {
        "job_description": job_description,
        "max_candidates": 10,
        "enable_multi_source": True,
        "include_score_breakdown": True
    }
    
    print(f"\n🔍 Searching for candidates...")
    print("(This may take 20-30 seconds)")
    
    try:
        # Send request
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/candidates", json=payload, headers=HEADERS)
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n🎉 SUCCESS! Found {data['total_candidates_found']} candidates")
            print(f"⏱️  Processing time: {data['processing_time']}s")
            print(f"📊 Top candidates returned: {len(data['top_candidates'])}")
            
            # Show top candidates
            print(f"\n🏆 TOP CANDIDATES:")
            print("=" * 50)
            
            for i, candidate in enumerate(data['top_candidates'][:10], 1):
                print(f"\n{i}. {candidate['name']}")
                print(f"   LinkedIn: {candidate['linkedin_url']}")
                print(f"   Headline: {candidate['headline']}")
                print(f"   Fit Score: {candidate['fit_score']}/10")
                
                if 'overall_confidence' in candidate:
                    print(f"   Confidence: {candidate['overall_confidence']:.2f}")
                
                if candidate['score_breakdown']:
                    breakdown = candidate['score_breakdown']
                    print(f"   Score Breakdown:")
                    for category, details in breakdown.items():
                        if isinstance(details, dict) and 'score' in details:
                            print(f"     - {category.title()}: {details['score']}/10")
                
                print(f"   Outreach Message:")
                print(f"     '{candidate['outreach_message']}'")
                print("-" * 30)
            
            # Show API response summary
            print(f"\n📋 API Response Summary:")
            print(f"   Total candidates found: {data['total_candidates_found']}")
            print(f"   Processing time: {data['processing_time']}s")
            
            # Save results to file
            filename = f"job_results_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"\n💾 Results saved to: {filename}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server!")
        print("Make sure the server is running with: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def demo_with_sample_jobs():
    """Demo with some sample job descriptions"""
    
    sample_jobs = [
        {
            "title": "Frontend React Developer",
            "description": "We're looking for a Senior Frontend Developer with React experience to join our team in San Francisco. Must have 3+ years of experience with React, TypeScript, and modern web development."
        },
        {
            "title": "Data Scientist",
            "description": "Data Scientist position at a fintech startup in New York. Looking for someone with Python, machine learning, and statistical analysis experience. Must have experience with pandas, scikit-learn, and SQL."
        },
        {
            "title": "DevOps Engineer",
            "description": "DevOps Engineer needed for a cloud-native company in Austin. Experience with AWS, Docker, Kubernetes, and CI/CD pipelines required. Must have experience with infrastructure as code."
        }
    ]
    
    print("🚀 Sample Job Demos")
    print("=" * 50)
    
    for i, job in enumerate(sample_jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   {job['description']}")
    
    choice = input(f"\nSelect a job (1-{len(sample_jobs)}) or press Enter to enter your own: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= len(sample_jobs):
        selected_job = sample_jobs[int(choice) - 1]
        print(f"\n✅ Selected: {selected_job['title']}")
        
        # Use the selected job
        payload = {
            "job_description": selected_job['description'],
            "max_candidates": 10,
            "enable_multi_source": True,
            "include_score_breakdown": True
        }
        
        print(f"\n🔍 Searching for candidates...")
        
        try:
            response = requests.post(f"{BASE_URL}/candidates", json=payload, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n🎉 Found {data['total_candidates_found']} candidates!")
                
                # Show first 3 candidates
                for i, candidate in enumerate(data['top_candidates'][:3], 1):
                    print(f"\n{i}. {candidate['name']} - Score: {candidate['fit_score']}/10")
                    print(f"   {candidate['linkedin_url']}")
                    print(f"   Message: {candidate['outreach_message']}")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        demo_with_custom_job()

if __name__ == "__main__":
    print("Welcome to LinkedIn Sourcing Agent Demo!")
    print("Choose an option:")
    print("1. Enter your own job description")
    print("2. Try sample job descriptions")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        demo_with_custom_job()
    elif choice == "2":
        demo_with_sample_jobs()
    else:
        print("Invalid choice. Running custom job demo...")
        demo_with_custom_job() 