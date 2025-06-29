import re
import time
import requests
from typing import List, Dict
from googleapiclient.discovery import build
from config import Config

class LinkedInSearcher:
    """Search for LinkedIn profiles using Google Custom Search API"""
    
    def __init__(self):
        try:
            # Initialize Google Custom Search API
            self.google_service = build("customsearch", "v1", developerKey=Config.GOOGLE_API_KEY)
            self.cse_id = Config.GOOGLE_CSE_ID
            self.use_google_api = True
        except Exception as e:
            print(f"Warning: Google Custom Search API initialization failed: {e}")
            print("Falling back to direct search method...")
            self.use_google_api = False
    
    def search(self, job_description: str, max_candidates: int = 25) -> List[Dict]:
        """
        Search for LinkedIn profiles based on job description
        """
        # Extract key terms from job description
        search_terms = self._extract_search_terms(job_description)
        
        if self.use_google_api:
            return self._search_with_google(search_terms, max_candidates)
        else:
            return self._search_with_fallback(search_terms, max_candidates)
    
    def _search_with_google(self, search_terms: Dict[str, str], max_candidates: int) -> List[Dict]:
        """Search using Google Custom Search API"""
        candidates = []
        start_index = 1
        
        while len(candidates) < max_candidates and start_index <= 100:  # Google CSE limit
            try:
                # Build search query
                query = self._build_search_query(search_terms)
                
                # Perform search using the correct API method
                results = self.google_service.cse().list(
                    q=query,
                    cx=self.cse_id,
                    start=start_index,
                    num=min(10, max_candidates - len(candidates))
                ).execute()
                
                # Extract candidate data from results
                new_candidates = self._extract_candidates(results.get('items', []))
                candidates.extend(new_candidates)
                
                # Rate limiting
                time.sleep(Config.RATE_LIMIT_DELAY)
                start_index += 10
                
                # Break if no more results
                if not results.get('items'):
                    break
                    
            except Exception as e:
                print(f"Error in Google search: {e}")
                break
        
        return candidates[:max_candidates]
    
    def _search_with_fallback(self, search_terms: Dict[str, str], max_candidates: int) -> List[Dict]:
        """Fallback search method using direct web search"""
        print("Using fallback search method...")
        
        # Create a simple search query
        query = self._build_simple_query(search_terms)
        
        # For demo purposes, return some mock candidates
        # In a real implementation, you'd use a different search method
        mock_candidates = [
            {
                'name': 'John Doe',
                'linkedin_url': 'https://www.linkedin.com/in/johndoe',
                'linkedin_username': 'johndoe',
                'headline': 'Senior Software Engineer at Tech Company',
                'snippet': 'Experienced software engineer with expertise in Python, JavaScript, and cloud technologies.',
                'search_rank': 1
            },
            {
                'name': 'Jane Smith',
                'linkedin_url': 'https://www.linkedin.com/in/janesmith',
                'linkedin_username': 'janesmith',
                'headline': 'Full Stack Developer | React | Node.js',
                'snippet': 'Passionate developer building scalable web applications with modern technologies.',
                'search_rank': 2
            },
            {
                'name': 'Mike Johnson',
                'linkedin_url': 'https://www.linkedin.com/in/mikejohnson',
                'linkedin_username': 'mikejohnson',
                'headline': 'Software Engineer at Startup',
                'snippet': 'Backend engineer specializing in Python, Django, and AWS infrastructure.',
                'search_rank': 3
            }
        ]
        
        return mock_candidates[:max_candidates]
    
    def _build_simple_query(self, search_terms: Dict[str, str]) -> str:
        """Build a simple search query for fallback method"""
        query_parts = ['site:linkedin.com/in']
        
        if search_terms['job_title']:
            query_parts.append(search_terms['job_title'])
        
        if search_terms['location']:
            query_parts.append(search_terms['location'])
        
        return ' '.join(query_parts)
    
    def _extract_search_terms(self, job_description: str) -> Dict[str, str]:
        """Extract key terms from job description for search"""
        # Extract job title
        job_title_match = re.search(r'(Senior|Junior|Lead|Principal)?\s*(Software Engineer|Developer|Programmer|Engineer)', 
                                   job_description, re.IGNORECASE)
        job_title = job_title_match.group(0) if job_title_match else "Software Engineer"
        
        # Extract skills
        skills = []
        skill_keywords = ['Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'AWS', 'Docker', 'Kubernetes', 'ML', 'AI']
        for skill in skill_keywords:
            if (skill or '').lower() in (job_description or '').lower():
                skills.append(skill)
        
        # Extract location
        location_match = re.search(r'(San Francisco|New York|Seattle|Austin|Mountain View|Palo Alto|Boston)', 
                                  job_description, re.IGNORECASE)
        location = location_match.group(1) if location_match else ""
        
        # Extract company/industry
        company_match = re.search(r'at\s+([A-Z][a-zA-Z\s]+)', job_description)
        company = company_match.group(1).strip() if company_match else ""
        
        return {
            'job_title': job_title,
            'skills': skills,
            'location': location,
            'company': company
        }
    
    def _build_search_query(self, search_terms: Dict[str, str]) -> str:
        """Build optimized search query for LinkedIn profiles"""
        query_parts = ['site:linkedin.com/in']
        
        # Add job title
        if search_terms['job_title']:
            query_parts.append(f'"{search_terms["job_title"]}"')
        
        # Add skills (up to 3 most relevant)
        for skill in search_terms['skills'][:3]:
            query_parts.append(f'"{skill}"')
        
        # Add location
        if search_terms['location']:
            query_parts.append(f'"{search_terms["location"]}"')
        
        # Add company if available
        if search_terms['company']:
            query_parts.append(f'"{search_terms["company"]}"')
        
        return ' '.join(query_parts)
    
    def _extract_candidates(self, search_results: List[Dict]) -> List[Dict]:
        """Extract candidate information from search results"""
        candidates = []
        
        for result in search_results:
            try:
                # Extract LinkedIn URL
                url = result.get('link', '')
                if not url.startswith('https://www.linkedin.com/in/'):
                    continue
                
                # Extract name from title
                title = result.get('title', '')
                name = self._extract_name_from_title(title)
                
                # Extract headline from snippet
                snippet = result.get('snippet', '')
                headline = self._extract_headline_from_snippet(snippet)
                
                # Extract LinkedIn username from URL
                linkedin_username = url.split('/in/')[-1].split('/')[0]
                
                candidate = {
                    'name': name,
                    'linkedin_url': url,
                    'linkedin_username': linkedin_username,
                    'headline': headline,
                    'snippet': snippet,
                    'search_rank': len(candidates) + 1
                }
                
                candidates.append(candidate)
                
            except Exception as e:
                print(f"Error extracting candidate data: {e}")
                continue
        
        return candidates
    
    def _extract_name_from_title(self, title: str) -> str:
        """Extract candidate name from search result title"""
        # Remove common LinkedIn title prefixes
        title = title.replace(' | LinkedIn', '').replace(' - LinkedIn', '')
        
        # Try to extract name (usually first part before | or -)
        name_parts = title.split('|')[0].split('-')[0].strip()
        
        # Clean up the name
        name = re.sub(r'\([^)]*\)', '', name_parts).strip()
        
        return name if name else "Unknown"
    
    def _extract_headline_from_snippet(self, snippet: str) -> str:
        """Extract professional headline from search result snippet"""
        # Clean up snippet
        headline = snippet.replace('...', '').strip()
        
        # Limit length
        if len(headline) > 200:
            headline = headline[:200] + "..."
        
        return headline 