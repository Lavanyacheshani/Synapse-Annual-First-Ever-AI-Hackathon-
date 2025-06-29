from .search import LinkedInSearcher
from .score import CandidateScorer
from .outreach import OutreachGenerator
from .cache import CacheManager
from .multi_source import MultiSourceEnhancer

class LinkedInSourcingAgent:
    """
    Enhanced autonomous AI agent that sources LinkedIn profiles, scores candidates,
    and generates personalized outreach messages with multi-source data enhancement.
    """
    
    def __init__(self):
        self.searcher = LinkedInSearcher()
        self.scorer = CandidateScorer()
        self.outreach_generator = OutreachGenerator()
        self.cache_manager = CacheManager()
        self.multi_source_enhancer = MultiSourceEnhancer()
    
    def process_job(self, job_description: str, max_candidates: int = 10, 
                   enable_multi_source: bool = True) -> dict:
        """
        Complete enhanced pipeline: search → enhance → score → generate outreach
        """
        print(f"🔍 Processing job: {job_description[:100]}...")
        
        # Step 1: Search for candidates
        candidates = self.search_linkedin(job_description, max_candidates)
        print(f"📊 Found {len(candidates)} candidates")
        
        # Step 2: Enhance with multi-source data (enhanced feature)
        enhancement_stats = {}
        if enable_multi_source:
            print("🔗 Starting multi-source enhancement...")
            enhanced_candidates = self.multi_source_enhancer.enhance_candidates(candidates)
            
            # Calculate enhancement statistics
            enhancement_stats = self._calculate_enhancement_stats(enhanced_candidates)
            print(f"✅ Enhanced {enhancement_stats['enhanced_count']}/{len(enhanced_candidates)} candidates")
            print(f"📈 Average enhancement score: {enhancement_stats['avg_enhancement_score']:.2f}")
        else:
            enhanced_candidates = candidates
            enhancement_stats = {
                'enhanced_count': 0,
                'avg_enhancement_score': 0.0,
                'sources_used': []
            }
        
        # Step 3: Score candidates with multi-source data
        scored_candidates = self.score_candidates(enhanced_candidates, job_description)
        print(f"🎯 Scored {len(scored_candidates)} candidates")
        
        # Step 4: Generate outreach messages
        outreach_candidates = self.generate_outreach(scored_candidates[:max_candidates], job_description)
        print(f"💬 Generated {len(outreach_candidates)} outreach messages")
        
        return {
            "job_description": job_description,
            "candidates_found": len(candidates),
            "candidates_scored": len(scored_candidates),
            "outreach_generated": len(outreach_candidates),
            "top_candidates": outreach_candidates,
            "total_candidates_found": len(candidates),  # For API compatibility
            "enhancement_stats": enhancement_stats,
            "multi_source_enabled": enable_multi_source
        }
    
    def _calculate_enhancement_stats(self, candidates: list) -> dict:
        """Calculate statistics about multi-source enhancement"""
        enhanced_count = sum(1 for c in candidates if c.get('multi_source_data'))
        enhancement_scores = [c.get('enhancement_score', 0.0) for c in candidates]
        avg_enhancement_score = sum(enhancement_scores) / len(enhancement_scores) if enhancement_scores else 0.0
        
        # Count sources used
        sources_used = set()
        for candidate in candidates:
            if candidate.get('multi_source_data'):
                sources_used.update(candidate['multi_source_data'].keys())
        
        return {
            'enhanced_count': enhanced_count,
            'avg_enhancement_score': round(avg_enhancement_score, 2),
            'sources_used': list(sources_used),
            'total_candidates': len(candidates)
        }
    
    def search_linkedin(self, job_description: str, max_candidates: int = 10) -> list:
        """Search for LinkedIn profiles based on job description"""
        return self.searcher.search(job_description, max_candidates)
    
    def score_candidates(self, candidates: list, job_description: str) -> list:
        """Score candidates using enhanced fit score algorithm with multi-source data"""
        return self.scorer.score_all(candidates, job_description)
    
    def generate_outreach(self, candidates: list, job_description: str) -> list:
        """Generate personalized outreach messages"""
        return self.outreach_generator.generate_all(candidates, job_description)
    
    def batch_process_jobs(self, job_descriptions: list, enable_multi_source: bool = True) -> list:
        """Process multiple jobs in parallel with multi-source enhancement"""
        import asyncio
        import aiohttp
        
        async def process_single_job(job_desc):
            return self.process_job(job_desc, enable_multi_source=enable_multi_source)
        
        async def process_all_jobs():
            tasks = [process_single_job(job) for job in job_descriptions]
            return await asyncio.gather(*tasks)
        
        return asyncio.run(process_all_jobs())
    
    def get_enhancement_details(self, candidate: dict) -> dict:
        """Get detailed information about multi-source enhancement for a candidate"""
        if not candidate.get('multi_source_data'):
            return {'enhanced': False, 'sources': [], 'scores': {}}
        
        multi_source_data = candidate['multi_source_data']
        scores = {}
        
        # Extract individual source scores
        for source in ['github', 'website', 'stackoverflow', 'medium', 'twitter']:
            if source in multi_source_data:
                scores[source] = candidate.get(f'{source}_score', 0.0)
        
        return {
            'enhanced': True,
            'sources': list(multi_source_data.keys()),
            'scores': scores,
            'overall_enhancement_score': candidate.get('enhancement_score', 0.0),
            'extracted_skills': candidate.get('extracted_skills', [])
        }

# Add alias for backward compatibility
LinkedInAgent = LinkedInSourcingAgent 