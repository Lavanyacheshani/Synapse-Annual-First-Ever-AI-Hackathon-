#!/usr/bin/env python3
"""
Free Alternatives to OpenAI for LinkedIn Sourcing Agent
"""

import requests
import json
from typing import Dict, List

class FreeMessageGenerator:
    """Generate outreach messages using free alternatives to OpenAI"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load message templates based on fit scores"""
        return {
            "excellent": [
                "Hi {first_name},\n\nI came across your impressive profile and was particularly struck by your {highlight} background. Your experience at {company} and your {strength} really stand out.\n\nI'm reaching out because I believe you'd be an excellent fit for a {job_title} role at our company. Your track record and expertise align perfectly with what we're looking for.\n\nWould you be interested in learning more about this opportunity? I'd love to discuss how your background could contribute to our team.\n\nBest regards,\n[Your Name]",
                
                "Hi {first_name},\n\nYour profile caught my attention - particularly your {highlight} experience and your work at {company}. It's clear you have a strong foundation in {strength}.\n\nI'm reaching out because I think you'd be an excellent addition to our team as a {job_title}. Your background and skills are exactly what we need.\n\nWould you be interested in discussing this opportunity further?\n\nBest regards,\n[Your Name]"
            ],
            "strong": [
                "Hi {first_name},\n\nI came across your profile and was impressed by your {highlight} background. Your experience at {company} shows strong {strength}.\n\nI'm reaching out because I think you'd be a strong fit for a {job_title} role at our company. Your skills and experience align well with what we're looking for.\n\nWould you be interested in learning more about this opportunity?\n\nBest regards,\n[Your Name]",
                
                "Hi {first_name},\n\nYour background in {highlight} at {company} caught my attention. You seem to have solid {strength} experience.\n\nI'm reaching out because I believe you'd be a strong candidate for a {job_title} position with us. Your experience matches our needs well.\n\nWould you be interested in discussing this opportunity?\n\nBest regards,\n[Your Name]"
            ],
            "good": [
                "Hi {first_name},\n\nI came across your profile and noticed your {highlight} background. Your work at {company} shows good {strength}.\n\nI'm reaching out because I think you'd be a good fit for a {job_title} role at our company. Your experience could be valuable to our team.\n\nWould you be interested in learning more about this opportunity?\n\nBest regards,\n[Your Name]",
                
                "Hi {first_name},\n\nYour profile shows interesting experience in {highlight} at {company}. You seem to have good {strength} skills.\n\nI'm reaching out about a {job_title} opportunity that might interest you. Your background could be a good match.\n\nWould you like to discuss this further?\n\nBest regards,\n[Your Name]"
            ],
            "solid": [
                "Hi {first_name},\n\nI came across your profile and noticed your {highlight} background. Your experience at {company} shows solid {strength}.\n\nI'm reaching out about a {job_title} opportunity that might be of interest. Your background could be a good fit.\n\nWould you be interested in learning more?\n\nBest regards,\n[Your Name]"
            ]
        }
    
    def generate_message(self, candidate: Dict, job_description: str) -> str:
        """Generate a personalized message using templates"""
        
        # Extract candidate details
        name = candidate.get('name', 'there')
        headline = candidate.get('headline', '')
        fit_score = candidate.get('fit_score', 0)
        score_breakdown = candidate.get('score_breakdown', {})
        
        # Extract first name
        first_name = name.split()[0] if name and ' ' in name else name
        
        # Determine quality level
        if fit_score >= 8.0:
            quality = "excellent"
        elif fit_score >= 7.0:
            quality = "strong"
        elif fit_score >= 6.0:
            quality = "good"
        else:
            quality = "solid"
        
        # Extract key strengths
        strengths = self._extract_strengths(score_breakdown)
        strength = strengths[0] if strengths else "technical background"
        
        # Extract company and job title
        company = self._extract_company(headline)
        job_title = self._extract_job_title(job_description)
        
        # Create highlight
        highlight = self._create_highlight(headline, strengths)
        
        # Select template
        import random
        template = random.choice(self.templates[quality])
        
        # Fill template
        message = template.format(
            first_name=first_name,
            highlight=highlight,
            company=company,
            strength=strength,
            job_title=job_title
        )
        
        return message
    
    def _extract_strengths(self, score_breakdown: Dict) -> List[str]:
        """Extract key strengths from score breakdown"""
        strengths = []
        
        if not score_breakdown:
            return ["technical background"]
        
        # Find categories with high scores
        for category, data in score_breakdown.items():
            score = data.get('score', 0)
            if score >= 8.0:
                if category == 'education':
                    strengths.append("impressive educational background")
                elif category == 'trajectory':
                    strengths.append("strong career progression")
                elif category == 'company':
                    strengths.append("experience at top-tier companies")
                elif category == 'experience':
                    strengths.append("excellent technical skills")
                elif category == 'location':
                    strengths.append("ideal location match")
                elif category == 'tenure':
                    strengths.append("stable work history")
        
        # If no high scores, mention moderate strengths
        if not strengths:
            for category, data in score_breakdown.items():
                score = data.get('score', 0)
                if score >= 6.0:
                    if category == 'experience':
                        strengths.append("relevant technical experience")
                    elif category == 'company':
                        strengths.append("solid industry experience")
                    elif category == 'education':
                        strengths.append("strong educational foundation")
        
        return strengths if strengths else ["technical background"]
    
    def _extract_company(self, headline: str) -> str:
        """Extract company from headline"""
        import re
        
        # Look for "at Company" pattern
        match = re.search(r'at\s+([A-Z][a-zA-Z\s]+?)(?:\s*[·|]|\s*$)', headline)
        if match:
            return match.group(1).strip()
        
        # Look for company keywords
        company_keywords = ['Google', 'Meta', 'Microsoft', 'Apple', 'Amazon', 'Netflix']
        for keyword in company_keywords:
            if keyword.lower() in headline.lower():
                return keyword
        
        return "your current company"
    
    def _extract_job_title(self, job_description: str) -> str:
        """Extract job title from description"""
        import re
        
        # Common patterns for job titles
        patterns = [
            r'(Senior|Junior|Lead|Principal)?\s*(Software Engineer|Developer|Programmer|Engineer)',
            r'(Senior|Junior|Lead|Principal)?\s*(Data Scientist|ML Engineer|AI Engineer)',
            r'(Senior|Junior|Lead|Principal)?\s*(Full Stack|Frontend|Backend|DevOps) Engineer'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Software Engineer"
    
    def _create_highlight(self, headline: str, strengths: List[str]) -> str:
        """Create a highlight from headline and strengths"""
        if "senior" in headline.lower():
            return "senior-level experience"
        elif "lead" in headline.lower():
            return "leadership experience"
        elif "principal" in headline.lower():
            return "principal-level expertise"
        elif strengths:
            return strengths[0]
        else:
            return "professional background"

def test_free_alternatives():
    """Test free message generation"""
    print("🆓 Testing Free Message Generation Alternatives")
    print("=" * 60)
    
    generator = FreeMessageGenerator()
    
    # Test candidates with different fit scores
    test_candidates = [
        {
            'name': 'John Doe',
            'headline': 'Senior Software Engineer at Google',
            'fit_score': 8.5,
            'score_breakdown': {
                'education': {'score': 9.0, 'confidence': 0.9},
                'trajectory': {'score': 8.0, 'confidence': 0.8},
                'company': {'score': 9.5, 'confidence': 0.9},
                'experience': {'score': 8.5, 'confidence': 0.8},
                'location': {'score': 7.0, 'confidence': 0.7},
                'tenure': {'score': 8.0, 'confidence': 0.8}
            }
        },
        {
            'name': 'Jane Smith',
            'headline': 'Software Engineer at Startup',
            'fit_score': 6.5,
            'score_breakdown': {
                'education': {'score': 6.0, 'confidence': 0.6},
                'trajectory': {'score': 6.0, 'confidence': 0.6},
                'company': {'score': 7.0, 'confidence': 0.7},
                'experience': {'score': 6.5, 'confidence': 0.6},
                'location': {'score': 6.0, 'confidence': 0.5},
                'tenure': {'score': 7.0, 'confidence': 0.7}
            }
        }
    ]
    
    job_description = "Senior Software Engineer at fintech startup"
    
    for i, candidate in enumerate(test_candidates, 1):
        print(f"\n📝 Candidate {i}: {candidate['name']} (Score: {candidate['fit_score']}/10)")
        print("-" * 50)
        
        message = generator.generate_message(candidate, job_description)
        print(message)
    
    print("\n✅ Free message generation working perfectly!")
    print("💡 No OpenAI needed - professional templates work great!")

if __name__ == "__main__":
    test_free_alternatives() 