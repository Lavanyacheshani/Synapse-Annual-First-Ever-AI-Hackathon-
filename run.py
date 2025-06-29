#!/usr/bin/env python3
"""
LinkedIn Sourcing Agent - Main Runner Script
Autonomous AI agent that sources LinkedIn profiles, scores candidates, and generates personalized outreach
"""

import argparse
import json
import sys
import time
from pathlib import Path

from agent import LinkedInSourcingAgent
from config import Config

def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn Sourcing Agent - Find and score candidates for job openings"
    )
    
    parser.add_argument(
        "--job", "-j",
        type=str,
        help="Job description to search for candidates"
    )
    
    parser.add_argument(
        "--job-file", "-f",
        type=str,
        help="Path to file containing job description"
    )
    
    parser.add_argument(
        "--max-candidates", "-m",
        type=int,
        default=25,
        help="Maximum number of candidates to find (default: 25)"
    )
    
    parser.add_argument(
        "--no-multi-source",
        action="store_true",
        help="Disable multi-source enhancement (GitHub, Twitter)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file to save results (JSON format)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--batch",
        type=str,
        help="Path to file containing multiple job descriptions (one per line)"
    )
    
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Show cache statistics"
    )
    
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all cached data"
    )
    
    parser.add_argument(
        "--demo-mode",
        action="store_true",
        help="Force demo mode with mock candidates (useful when APIs are not working)"
    )
    
    args = parser.parse_args()
    
    # Validate API keys first
    try:
        Config.validate_keys()
        print("✅ API keys validated successfully")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please check your .env file and ensure all required API keys are set.")
        sys.exit(1)
    
    # Initialize agent
    agent = LinkedInSourcingAgent()
    
    # Handle cache operations
    if args.cache_stats:
        stats = agent.cache_manager.get_cache_stats()
        print("\n📊 Cache Statistics:")
        print(json.dumps(stats, indent=2))
        return
    
    if args.clear_cache:
        agent.cache_manager.clear_all_cache()
        print("🗑️ Cache cleared successfully")
        return
    
    # Get job description
    job_description = None
    
    if args.job:
        job_description = args.job
    elif args.job_file:
        try:
            with open(args.job_file, 'r', encoding='utf-8') as f:
                job_description = f.read().strip()
        except FileNotFoundError:
            print(f"❌ Error: Job file '{args.job_file}' not found")
            sys.exit(1)
    elif args.batch:
        # Handle batch processing
        try:
            with open(args.batch, 'r', encoding='utf-8') as f:
                job_descriptions = [line.strip() for line in f if line.strip()]
            
            print(f"🚀 Processing {len(job_descriptions)} jobs in batch...")
            
            start_time = time.time()
            results = agent.batch_process_jobs(job_descriptions)
            total_time = time.time() - start_time
            
            print(f"✅ Batch processing completed in {total_time:.2f} seconds")
            
            # Save results
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                print(f"💾 Results saved to {args.output}")
            else:
                print("\n📋 Batch Results Summary:")
                for i, result in enumerate(results):
                    print(f"\nJob {i+1}: {result['job_description'][:100]}...")
                    print(f"  Candidates found: {result['candidates_found']}")
                    print(f"  Top candidate score: {result['top_candidates'][0]['fit_score'] if result['top_candidates'] else 'N/A'}")
            
            return
            
        except FileNotFoundError:
            print(f"❌ Error: Batch file '{args.batch}' not found")
            sys.exit(1)
    else:
        # Interactive mode
        print("🎯 LinkedIn Sourcing Agent")
        print("=" * 50)
        print("Enter a job description to find candidates:")
        job_description = input("> ").strip()
        
        if not job_description:
            print("❌ No job description provided")
            sys.exit(1)
    
    # Check if we're in demo mode or if APIs are not working
    if args.demo_mode or not agent.searcher.use_google_api:
        print("\n🎭 DEMO MODE: Using mock candidates for demonstration")
        print("💡 To use real LinkedIn search, enable Google Custom Search API")
        print("   Visit: https://console.developers.google.com/apis/api/customsearch.googleapis.com/overview")
        print()
    
    # Process the job
    print(f"\n🔍 Processing job: {job_description[:100]}...")
    
    start_time = time.time()
    
    try:
        result = agent.process_job(
            job_description=job_description,
            max_candidates=args.max_candidates,
            enable_multi_source=not args.no_multi_source
        )
        
        processing_time = time.time() - start_time
        
        # Display results
        print(f"\n✅ Processing completed in {processing_time:.2f} seconds")
        print(f"📊 Found {result['candidates_found']} candidates")
        print(f"🎯 Scored {result['candidates_scored']} candidates")
        print(f"💬 Generated {result['outreach_generated']} outreach messages")
        
        # Show top candidates
        print(f"\n🏆 Top {len(result['top_candidates'])} Candidates:")
        print("=" * 80)
        
        for i, candidate in enumerate(result['top_candidates'], 1):
            print(f"\n{i}. {candidate['name']}")
            print(f"   LinkedIn: {candidate['linkedin_url']}")
            print(f"   Headline: {candidate['headline']}")
            print(f"   Fit Score: {candidate['fit_score']}/10 (Confidence: {candidate['overall_confidence']:.2f})")
            
            if args.verbose and candidate.get('score_breakdown'):
                print("   Score Breakdown:")
                for category, data in candidate['score_breakdown'].items():
                    print(f"     {category.title()}: {data['score']:.1f} (Confidence: {data['confidence']:.2f})")
            
            if not args.no_multi_source and candidate.get('enhancement_score'):
                print(f"   Enhancement Score: {candidate['enhancement_score']}/10")
            
            print(f"   Outreach Message:")
            print(f"   {candidate['outreach_message'][:200]}...")
            print("-" * 80)
        
        # Save results if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to {args.output}")
        
        # Show next steps if in demo mode
        if args.demo_mode or not agent.searcher.use_google_api:
            print(f"\n💡 To get real LinkedIn candidates:")
            print("   1. Enable Google Custom Search API")
            print("   2. Add billing to OpenAI account")
            print("   3. Run: python run.py --job 'your job description'")
        
    except Exception as e:
        print(f"❌ Error processing job: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 