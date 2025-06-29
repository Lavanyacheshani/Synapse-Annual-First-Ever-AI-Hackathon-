import json
import time
import hashlib
import os
from typing import Dict, Any, Optional
from tinydb import TinyDB, Query
from config import Config

class CacheManager:
    """Smart caching system to avoid re-fetching data"""
    
    def __init__(self):
        # Get the project root directory (parent of agent directory)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cache_path = os.path.join(project_root, 'data', 'cache.json')
        self.db = TinyDB(cache_path)
        self.candidates_table = self.db.table('candidates')
        self.search_results_table = self.db.table('search_results')
        self.expiry_hours = Config.CACHE_EXPIRY_HOURS
    
    def get_cached_candidates(self, job_description: str) -> Optional[list]:
        """Get cached candidates for a job description"""
        cache_key = self._generate_cache_key(job_description)
        
        # Check if we have cached results
        cached = self.search_results_table.search(Query().cache_key == cache_key)
        
        if cached:
            cache_entry = cached[0]
            
            # Check if cache is still valid
            if self._is_cache_valid(cache_entry['timestamp']):
                print(f"📦 Using cached results for job search")
                return cache_entry['candidates']
            else:
                # Remove expired cache
                self.search_results_table.remove(Query().cache_key == cache_key)
        
        return None
    
    def cache_candidates(self, job_description: str, candidates: list) -> None:
        """Cache candidates for a job description"""
        cache_key = self._generate_cache_key(job_description)
        
        # Store search results
        self.search_results_table.insert({
            'cache_key': cache_key,
            'job_description': job_description,
            'candidates': candidates,
            'timestamp': time.time(),
            'count': len(candidates)
        })
        
        # Store individual candidates for reuse
        for candidate in candidates:
            candidate_key = self._generate_candidate_key(candidate)
            
            # Check if candidate already exists
            existing = self.candidates_table.search(Query().candidate_key == candidate_key)
            
            if not existing:
                self.candidates_table.insert({
                    'candidate_key': candidate_key,
                    'candidate_data': candidate,
                    'timestamp': time.time(),
                    'access_count': 1
                })
            else:
                # Update access count and timestamp
                self.candidates_table.update({
                    'access_count': existing[0]['access_count'] + 1,
                    'timestamp': time.time()
                }, Query().candidate_key == candidate_key)
        
        print(f"💾 Cached {len(candidates)} candidates")
    
    def get_cached_candidate(self, linkedin_url: str) -> Optional[Dict]:
        """Get cached candidate data by LinkedIn URL"""
        candidate_key = self._generate_candidate_key({'linkedin_url': linkedin_url})
        
        cached = self.candidates_table.search(Query().candidate_key == candidate_key)
        
        if cached:
            cache_entry = cached[0]
            
            # Check if cache is still valid
            if self._is_cache_valid(cache_entry['timestamp']):
                return cache_entry['candidate_data']
            else:
                # Remove expired cache
                self.candidates_table.remove(Query().candidate_key == candidate_key)
        
        return None
    
    def cache_candidate(self, candidate: Dict) -> None:
        """Cache individual candidate data"""
        candidate_key = self._generate_candidate_key(candidate)
        
        # Check if candidate already exists
        existing = self.candidates_table.search(Query().candidate_key == candidate_key)
        
        if not existing:
            self.candidates_table.insert({
                'candidate_key': candidate_key,
                'candidate_data': candidate,
                'timestamp': time.time(),
                'access_count': 1
            })
        else:
            # Update access count and timestamp
            self.candidates_table.update({
                'access_count': existing[0]['access_count'] + 1,
                'timestamp': time.time()
            }, Query().candidate_key == candidate_key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_candidates = len(self.candidates_table)
        total_searches = len(self.search_results_table)
        
        # Calculate cache hit rate (simplified)
        total_accesses = sum(
            entry['access_count'] for entry in self.candidates_table.all()
        )
        
        # Get most accessed candidates
        all_candidates = self.candidates_table.all()
        most_accessed = sorted(
            all_candidates, 
            key=lambda x: x['access_count'], 
            reverse=True
        )[:5]
        
        return {
            'total_cached_candidates': total_candidates,
            'total_cached_searches': total_searches,
            'total_accesses': total_accesses,
            'most_accessed_candidates': [
                {
                    'name': candidate['candidate_data'].get('name', 'Unknown'),
                    'access_count': candidate['access_count']
                }
                for candidate in most_accessed
            ]
        }
    
    def clear_expired_cache(self) -> int:
        """Clear expired cache entries and return count of cleared items"""
        current_time = time.time()
        expiry_seconds = self.expiry_hours * 3600
        
        # Clear expired search results
        expired_searches = self.search_results_table.search(
            Query().timestamp < (current_time - expiry_seconds)
        )
        for search in expired_searches:
            self.search_results_table.remove(Query().cache_key == search['cache_key'])
        
        # Clear expired candidates
        expired_candidates = self.candidates_table.search(
            Query().timestamp < (current_time - expiry_seconds)
        )
        for candidate in expired_candidates:
            self.candidates_table.remove(Query().candidate_key == candidate['candidate_key'])
        
        cleared_count = len(expired_searches) + len(expired_candidates)
        
        if cleared_count > 0:
            print(f"🧹 Cleared {cleared_count} expired cache entries")
        
        return cleared_count
    
    def clear_all_cache(self) -> None:
        """Clear all cached data"""
        self.candidates_table.truncate()
        self.search_results_table.truncate()
        print("🗑️ Cleared all cached data")
    
    def _generate_cache_key(self, job_description: str) -> str:
        """Generate a unique cache key for job description"""
        # Create a hash of the job description
        hash_object = hashlib.md5(job_description.encode())
        return hash_object.hexdigest()
    
    def _generate_candidate_key(self, candidate: Dict) -> str:
        """Generate a unique cache key for candidate"""
        # Use LinkedIn URL as the primary identifier
        linkedin_url = candidate.get('linkedin_url', '')
        if linkedin_url:
            hash_object = hashlib.md5(linkedin_url.encode())
            return hash_object.hexdigest()
        
        # Fallback to name and headline
        name = candidate.get('name', '')
        headline = candidate.get('headline', '')
        combined = f"{name}:{headline}"
        hash_object = hashlib.md5(combined.encode())
        return hash_object.hexdigest()
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cache entry is still valid"""
        current_time = time.time()
        expiry_seconds = self.expiry_hours * 3600
        return (current_time - timestamp) < expiry_seconds 