import re
from typing import List, Dict, Tuple
from config import Config

class CandidateScorer:
    """Enhanced candidate scorer that integrates multi-source data"""
    
    def __init__(self):
        self.elite_schools = Config.ELITE_SCHOOLS
        self.top_tech_companies = Config.TOP_TECH_COMPANIES
    
    def score_all(self, candidates: List[Dict], job_description: str) -> List[Dict]:
        """Score all candidates and add confidence levels with multi-source enhancement"""
        scored_candidates = []
        
        for candidate in candidates:
            score_result = self.score_candidate(candidate, job_description)
            candidate.update(score_result)
            scored_candidates.append(candidate)
        
        # Sort by fit score (highest first)
        scored_candidates.sort(key=lambda x: x.get('fit_score', 0), reverse=True)
        
        return scored_candidates
    
    def score_candidate(self, candidate: Dict, job_description: str) -> Dict:
        """Score a single candidate using enhanced fit score rubric with multi-source data"""
        
        # Extract candidate data
        headline = (candidate.get('headline') or '').lower()
        snippet = (candidate.get('snippet') or '').lower()
        name = candidate.get('name', '')
        
        # Get multi-source data if available
        multi_source_data = candidate.get('multi_source_data', {})
        extracted_skills = candidate.get('extracted_skills', [])
        enhancement_score = candidate.get('enhancement_score', 0.0)
        
        # Score each category with multi-source enhancement
        education_score, education_confidence = self._score_education(headline, snippet, multi_source_data)
        trajectory_score, trajectory_confidence = self._score_career_trajectory(headline, snippet, multi_source_data)
        company_score, company_confidence = self._score_company_relevance(headline, snippet, multi_source_data)
        experience_score, experience_confidence = self._score_experience_match(headline, snippet, job_description, extracted_skills, multi_source_data)
        location_score, location_confidence = self._score_location_match(headline, snippet, job_description, multi_source_data)
        tenure_score, tenure_confidence = self._score_tenure(headline, snippet, multi_source_data)
        
        # Add multi-source enhancement score as a new category
        multi_source_score, multi_source_confidence = self._score_multi_source_enhancement(enhancement_score, multi_source_data)
        
        # Calculate weighted fit score with multi-source enhancement
        weights = {
            'education': 0.15,
            'trajectory': 0.15,
            'company': 0.10,
            'experience': 0.25,
            'location': 0.10,
            'tenure': 0.10,
            'multi_source': 0.15  # New category for multi-source enhancement
        }
        
        fit_score = (
            education_score * weights['education'] +
            trajectory_score * weights['trajectory'] +
            company_score * weights['company'] +
            experience_score * weights['experience'] +
            location_score * weights['location'] +
            tenure_score * weights['tenure'] +
            multi_source_score * weights['multi_source']
        )
        
        # Calculate overall confidence
        confidences = [
            education_confidence, trajectory_confidence, company_confidence,
            experience_confidence, location_confidence, tenure_confidence,
            multi_source_confidence
        ]
        overall_confidence = sum(confidences) / len(confidences)
        
        return {
            'fit_score': round(fit_score, 2),
            'overall_confidence': round(overall_confidence, 2),
            'score_breakdown': {
                'education': {
                    'score': education_score,
                    'confidence': education_confidence,
                    'weight': weights['education'],
                    'enhanced_by': self._get_enhancement_sources('education', multi_source_data)
                },
                'trajectory': {
                    'score': trajectory_score,
                    'confidence': trajectory_confidence,
                    'weight': weights['trajectory'],
                    'enhanced_by': self._get_enhancement_sources('trajectory', multi_source_data)
                },
                'company': {
                    'score': company_score,
                    'confidence': company_confidence,
                    'weight': weights['company'],
                    'enhanced_by': self._get_enhancement_sources('company', multi_source_data)
                },
                'experience': {
                    'score': experience_score,
                    'confidence': experience_confidence,
                    'weight': weights['experience'],
                    'enhanced_by': self._get_enhancement_sources('experience', multi_source_data)
                },
                'location': {
                    'score': location_score,
                    'confidence': location_confidence,
                    'weight': weights['location'],
                    'enhanced_by': self._get_enhancement_sources('location', multi_source_data)
                },
                'tenure': {
                    'score': tenure_score,
                    'confidence': tenure_confidence,
                    'weight': weights['tenure'],
                    'enhanced_by': self._get_enhancement_sources('tenure', multi_source_data)
                },
                'multi_source': {
                    'score': multi_source_score,
                    'confidence': multi_source_confidence,
                    'weight': weights['multi_source'],
                    'sources_used': list(multi_source_data.keys()) if multi_source_data else []
                }
            }
        }
    
    def _score_education(self, headline: str, snippet: str, multi_source_data: Dict) -> Tuple[float, float]:
        """Score education with multi-source enhancement"""
        text = f"{headline} {snippet}".lower()
        base_score, base_confidence = self._score_education_base(text)
        
        # Enhance with multi-source data
        enhancement_bonus = 0.0
        confidence_boost = 0.0
        
        # GitHub bio might contain education info
        if 'github' in multi_source_data:
            github_bio = (multi_source_data['github'].get('bio') or '').lower()
            if any((school or '').lower() in github_bio for school in self.elite_schools):
                enhancement_bonus += 1.0
                confidence_boost += 0.1
        
        # Website might mention education
        if 'website' in multi_source_data:
            website_content = (multi_source_data['website'].get('description') or '').lower()
            if any((school or '').lower() in website_content for school in self.elite_schools):
                enhancement_bonus += 0.5
                confidence_boost += 0.05
        
        final_score = min(base_score + enhancement_bonus, 10.0)
        final_confidence = min(base_confidence + confidence_boost, 1.0)
        
        return final_score, final_confidence
    
    def _score_education_base(self, text: str) -> Tuple[float, float]:
        """Base education scoring logic"""
        # Check for elite schools
        for school in self.elite_schools:
            if (school or '').lower() in text:
                return 9.5, 0.9  # High confidence for elite schools
        
        # Check for strong schools
        strong_schools = ['university', 'college', 'bachelor', 'master', 'phd']
        if any((school or '') in text for school in strong_schools):
            return 7.0, 0.7
        
        # Check for clear progression (degree mentioned)
        if any((degree or '') in text for degree in ['b.s.', 'm.s.', 'phd', 'bachelor', 'master']):
            return 8.0, 0.8
        
        return 5.0, 0.3  # Low confidence, assume standard education
    
    def _score_career_trajectory(self, headline: str, snippet: str, multi_source_data: Dict) -> Tuple[float, float]:
        """Score career trajectory with multi-source enhancement"""
        text = f"{headline} {snippet}".lower()
        base_score, base_confidence = self._score_trajectory_base(text)
        
        # Enhance with multi-source data
        enhancement_bonus = 0.0
        confidence_boost = 0.0
        
        # GitHub activity can indicate career progression
        if 'github' in multi_source_data:
            github_data = multi_source_data['github']
            followers = github_data.get('followers', 0)
            repos = github_data.get('public_repos', 0)
            
            if followers >= 500 or repos >= 20:
                enhancement_bonus += 0.5
                confidence_boost += 0.05
        
        # Website portfolio can show career progression
        if 'website' in multi_source_data:
            website_data = multi_source_data['website']
            if website_data.get('has_portfolio', False):
                enhancement_bonus += 0.5
                confidence_boost += 0.05
        
        final_score = min(base_score + enhancement_bonus, 10.0)
        final_confidence = min(base_confidence + confidence_boost, 1.0)
        
        return final_score, final_confidence
    
    def _score_trajectory_base(self, text: str) -> Tuple[float, float]:
        """Base career trajectory scoring logic"""
        # Check for senior/lead/principal positions
        senior_indicators = ['senior', 'lead', 'principal', 'staff', 'director', 'manager']
        if any((indicator or '') in text for indicator in senior_indicators):
            return 8.0, 0.8
        
        # Check for steady progression indicators
        progression_indicators = ['promoted', 'growth', 'advancement', 'progression']
        if any((indicator or '') in text for indicator in progression_indicators):
            return 7.0, 0.7
        
        # Check for junior positions
        junior_indicators = ['junior', 'entry', 'associate', 'intern']
        if any((indicator or '') in text for indicator in junior_indicators):
            return 4.0, 0.6
        
        return 6.0, 0.4  # Medium confidence, assume steady growth
    
    def _score_company_relevance(self, headline: str, snippet: str, multi_source_data: Dict) -> Tuple[float, float]:
        """Score company relevance with multi-source enhancement"""
        text = f"{headline} {snippet}".lower()
        base_score, base_confidence = self._score_company_base(text)
        
        # Enhance with multi-source data
        enhancement_bonus = 0.0
        confidence_boost = 0.0
        
        # GitHub company field
        if 'github' in multi_source_data:
            github_company = (multi_source_data['github'].get('company') or '').lower()
            if any((company or '').lower() in github_company for company in self.top_tech_companies):
                enhancement_bonus += 1.0
                confidence_boost += 0.1
        
        # Website might mention current company
        if 'website' in multi_source_data:
            website_content = (multi_source_data['website'].get('description') or '').lower()
            if any((company or '').lower() in website_content for company in self.top_tech_companies):
                enhancement_bonus += 0.5
                confidence_boost += 0.05
        
        final_score = min(base_score + enhancement_bonus, 10.0)
        final_confidence = min(base_confidence + confidence_boost, 1.0)
        
        return final_score, final_confidence
    
    def _score_company_base(self, text: str) -> Tuple[float, float]:
        """Base company relevance scoring logic"""
        # Check for top tech companies
        for company in self.top_tech_companies:
            if (company or '').lower() in text:
                return 9.5, 0.9
        
        # Check for relevant industry keywords
        tech_indicators = ['tech', 'software', 'startup', 'ai', 'ml', 'fintech', 'saas']
        if any((indicator or '') in text for indicator in tech_indicators):
            return 7.5, 0.7
        
        # Check for any company experience
        company_indicators = ['at', 'company', 'inc', 'corp', 'ltd']
        if any((indicator or '') in text for indicator in company_indicators):
            return 5.5, 0.6
        
        return 4.0, 0.3  # Low confidence, limited company info
    
    def _score_experience_match(self, headline: str, snippet: str, job_description: str, 
                              extracted_skills: List[str], multi_source_data: Dict) -> Tuple[float, float]:
        """Score experience match with multi-source enhancement"""
        candidate_text = f"{headline} {snippet}".lower()
        job_text = (job_description or '').lower()
        
        # Extract skills from job description
        job_skills = self._extract_skills_from_job(job_text)
        candidate_skills = self._extract_skills_from_candidate(candidate_text)
        
        # Add skills from multi-source data
        candidate_skills.extend(extracted_skills)
        
        if not job_skills:
            return 6.0, 0.4  # Can't determine without job skills
        
        # Calculate skill overlap
        overlap = len(set(job_skills) & set(candidate_skills))
        total_job_skills = len(job_skills)
        
        if total_job_skills == 0:
            return 6.0, 0.4
        
        skill_match_ratio = overlap / total_job_skills
        
        # Base score from skill match
        if skill_match_ratio >= 0.8:
            base_score, base_confidence = 9.5, 0.9
        elif skill_match_ratio >= 0.6:
            base_score, base_confidence = 8.0, 0.8
        elif skill_match_ratio >= 0.4:
            base_score, base_confidence = 6.5, 0.7
        elif skill_match_ratio >= 0.2:
            base_score, base_confidence = 5.0, 0.6
        else:
            base_score, base_confidence = 3.0, 0.5
        
        # Enhance with multi-source data
        enhancement_bonus = 0.0
        confidence_boost = 0.0
        
        # GitHub repositories can show technical expertise
        if 'github' in multi_source_data:
            github_data = multi_source_data['github']
            top_repos = github_data.get('top_repos', [])
            total_stars = sum(repo.get('stars', 0) for repo in top_repos)
            
            if total_stars >= 100:
                enhancement_bonus += 0.5
                confidence_boost += 0.05
            
            # Check if GitHub languages match job requirements
            languages = github_data.get('languages_used', {})
            if any((lang or '').lower() in job_text for lang in languages.keys()):
                enhancement_bonus += 0.5
                confidence_boost += 0.05
        
        # Stack Overflow reputation can indicate expertise
        if 'stackoverflow' in multi_source_data:
            stackoverflow_data = multi_source_data['stackoverflow']
            reputation = stackoverflow_data.get('reputation', 0)
            
            if reputation >= 1000:
                enhancement_bonus += 0.5
                confidence_boost += 0.05
        
        # Website technologies can show relevant experience
        if 'website' in multi_source_data:
            website_data = multi_source_data['website']
            tech_mentioned = website_data.get('technologies_mentioned', [])
            
            if any((tech or '').lower() in job_text for tech in tech_mentioned):
                enhancement_bonus += 0.5
                confidence_boost += 0.05
        
        final_score = min(base_score + enhancement_bonus, 10.0)
        final_confidence = min(base_confidence + confidence_boost, 1.0)
        
        return final_score, final_confidence
    
    def _score_location_match(self, headline: str, snippet: str, job_description: str, 
                            multi_source_data: Dict) -> Tuple[float, float]:
        """Score location match with multi-source enhancement"""
        candidate_text = f"{headline} {snippet}".lower()
        job_text = (job_description or '').lower()
        
        # Extract locations
        job_locations = self._extract_locations(job_text)
        candidate_locations = self._extract_locations(candidate_text)
        
        # Add locations from multi-source data
        if 'github' in multi_source_data:
            github_location = multi_source_data['github'].get('location')
            if github_location:
                candidate_locations.append((github_location or '').lower())
        
        if not job_locations:
            return 6.0, 0.3  # Remote-friendly if no location specified
        
        if not candidate_locations:
            return 6.0, 0.3  # Assume remote-friendly
        
        # Check for exact city match
        for job_loc in job_locations:
            for candidate_loc in candidate_locations:
                if (job_loc or '').lower() == (candidate_loc or '').lower():
                    return 10.0, 0.9  # Exact match
        
        # Check for same metro area
        metro_areas = {
            'san francisco': ['mountain view', 'palo alto', 'san jose', 'oakland'],
            'new york': ['brooklyn', 'queens', 'manhattan', 'bronx'],
            'seattle': ['bellevue', 'redmond', 'kirkland'],
            'austin': ['round rock', 'cedar park'],
            'boston': ['cambridge', 'somerville', 'waltham']
        }
        
        for metro, cities in metro_areas.items():
            if any((loc or '').lower() in metro for loc in job_locations):
                if any((loc or '').lower() in cities for loc in candidate_locations):
                    return 8.0, 0.8  # Same metro area
        
        return 4.0, 0.5  # Different locations
    
    def _score_tenure(self, headline: str, snippet: str, multi_source_data: Dict) -> Tuple[float, float]:
        """Score tenure with multi-source enhancement"""
        text = f"{headline} {snippet}".lower()
        base_score, base_confidence = self._score_tenure_base(text)
        
        # Enhance with multi-source data
        enhancement_bonus = 0.0
        confidence_boost = 0.0
        
        # GitHub account age can indicate professional longevity
        if 'github' in multi_source_data:
            github_data = multi_source_data['github']
            created_at = github_data.get('created_at', '')
            
            if created_at:
                import datetime
                try:
                    created_date = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    age_years = (datetime.datetime.now(datetime.timezone.utc) - created_date).days / 365
                    
                    if age_years >= 5:
                        enhancement_bonus += 0.5
                        confidence_boost += 0.05
                    elif age_years >= 3:
                        enhancement_bonus += 0.3
                        confidence_boost += 0.03
                except:
                    pass
        
        final_score = min(base_score + enhancement_bonus, 10.0)
        final_confidence = min(base_confidence + confidence_boost, 1.0)
        
        return final_score, final_confidence
    
    def _score_tenure_base(self, text: str) -> Tuple[float, float]:
        """Base tenure scoring logic"""
        # Look for tenure indicators
        tenure_patterns = [
            r'(\d+)\s*years?',
            r'(\d+)\s*yr',
            r'(\d+)\s*months?',
            r'(\d+)\s*mo'
        ]
        
        for pattern in tenure_patterns:
            matches = re.findall(pattern, text)
            if matches:
                years = sum(int(match) for match in matches)
                if 2 <= years <= 3:
                    return 9.0, 0.8  # Ideal tenure
                elif 1 <= years < 2:
                    return 7.0, 0.7  # Good tenure
                elif years > 3:
                    return 6.0, 0.6  # Long tenure
                else:
                    return 4.0, 0.5  # Short tenure
        
        # Check for job hopping indicators
        hopping_indicators = ['multiple', 'various', 'several', 'different']
        if any((indicator or '') in text for indicator in hopping_indicators):
            return 3.0, 0.4  # Potential job hopping
        
        return 6.0, 0.3  # Unknown tenure, neutral score
    
    def _score_multi_source_enhancement(self, enhancement_score: float, multi_source_data: Dict) -> Tuple[float, float]:
        """Score based on multi-source enhancement quality"""
        if not multi_source_data:
            return 0.0, 0.0
        
        # Base score from enhancement score (0-10)
        base_score = enhancement_score
        
        # Confidence based on number of sources
        sources_count = len(multi_source_data)
        if sources_count >= 4:
            confidence = 0.9
        elif sources_count >= 3:
            confidence = 0.8
        elif sources_count >= 2:
            confidence = 0.7
        else:
            confidence = 0.6
        
        # Bonus for high-quality sources
        quality_bonus = 0.0
        if 'github' in multi_source_data:
            quality_bonus += 0.5
        if 'website' in multi_source_data:
            quality_bonus += 0.3
        if 'stackoverflow' in multi_source_data:
            quality_bonus += 0.2
        
        final_score = min(base_score + quality_bonus, 10.0)
        
        return final_score, confidence
    
    def _get_enhancement_sources(self, category: str, multi_source_data: Dict) -> List[str]:
        """Get list of sources that enhanced a particular category"""
        sources = []
        
        if not multi_source_data:
            return sources
        
        if category == 'education' and ('github' in multi_source_data or 'website' in multi_source_data):
            sources.extend([k for k in ['github', 'website'] if k in multi_source_data])
        
        elif category == 'trajectory' and ('github' in multi_source_data or 'website' in multi_source_data):
            sources.extend([k for k in ['github', 'website'] if k in multi_source_data])
        
        elif category == 'company' and ('github' in multi_source_data or 'website' in multi_source_data):
            sources.extend([k for k in ['github', 'website'] if k in multi_source_data])
        
        elif category == 'experience' and any(k in multi_source_data for k in ['github', 'stackoverflow', 'website']):
            sources.extend([k for k in ['github', 'stackoverflow', 'website'] if k in multi_source_data])
        
        elif category == 'location' and 'github' in multi_source_data:
            sources.append('github')
        
        elif category == 'tenure' and 'github' in multi_source_data:
            sources.append('github')
        
        return sources
    
    def _extract_skills_from_job(self, job_text: str) -> List[str]:
        """Extract skills from job description"""
        skills = []
        skill_keywords = [
            'python', 'javascript', 'java', 'c++', 'react', 'node.js', 'aws', 
            'docker', 'kubernetes', 'machine learning', 'ai', 'ml', 'tensorflow',
            'pytorch', 'sql', 'mongodb', 'postgresql', 'redis', 'kafka',
            'microservices', 'api', 'rest', 'graphql', 'git', 'jenkins',
            'terraform', 'ansible', 'linux', 'unix', 'agile', 'scrum',
            'typescript', 'vue', 'angular', 'php', 'ruby', 'go', 'rust',
            'swift', 'kotlin', 'scala', 'elasticsearch', 'data science',
            'blockchain', 'devops', 'ci/cd', 'testing', 'tdd', 'bdd'
        ]
        
        for skill in skill_keywords:
            if skill in job_text:
                skills.append(skill)
        
        return skills
    
    def _extract_skills_from_candidate(self, candidate_text: str) -> List[str]:
        """Extract skills from candidate profile"""
        return self._extract_skills_from_job(candidate_text)
    
    def _extract_locations(self, text: str) -> List[str]:
        """Extract location mentions from text"""
        locations = []
        location_patterns = [
            r'san francisco',
            r'new york',
            r'seattle',
            r'austin',
            r'mountain view',
            r'palo alto',
            r'boston',
            r'los angeles',
            r'chicago',
            r'denver',
            r'atlanta',
            r'miami',
            r'portland',
            r'san diego',
            r'phoenix',
            r'las vegas',
            r'houston',
            r'dallas',
            r'philadelphia',
            r'washington dc'
        ]
        
        for pattern in location_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                locations.append(pattern.replace('\\', ''))
        
        return locations 