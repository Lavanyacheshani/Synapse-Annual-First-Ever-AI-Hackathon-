import openai
from typing import List, Dict
from config import Config

class OutreachGenerator:
    """Generate personalized outreach messages using OpenAI"""
    
    def __init__(self):
        if Config.USE_OPENAI and Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            self.use_openai = True
        else:
            self.use_openai = False
            print("⚠️ OpenAI disabled - using fallback messages")
    
    def generate_all(self, candidates: List[Dict], job_description: str) -> List[Dict]:
        """Generate personalized outreach messages for all candidates"""
        outreach_candidates = []
        
        for candidate in candidates:
            try:
                if self.use_openai and not Config.USE_FALLBACK_MESSAGES:
                    message = self.generate_message(candidate, job_description)
                else:
                    message = self._generate_fallback_message(candidate, job_description)
                
                candidate['outreach_message'] = message
                outreach_candidates.append(candidate)
            except Exception as e:
                print(f"Error generating message for {candidate.get('name', 'Unknown')}: {e}")
                # Fallback message
                candidate['outreach_message'] = self._generate_fallback_message(candidate, job_description)
                outreach_candidates.append(candidate)
        
        return outreach_candidates
    
    def generate_message(self, candidate: Dict, job_description: str) -> str:
        """Generate a personalized outreach message for a candidate"""
        
        # Extract candidate details
        name = candidate.get('name', 'there')
        headline = candidate.get('headline', '')
        fit_score = candidate.get('fit_score', 0)
        score_breakdown = candidate.get('score_breakdown', {})
        
        # Extract key strengths from score breakdown
        strengths = self._extract_strengths(score_breakdown)
        
        # Create prompt for OpenAI
        prompt = self._create_prompt(name, headline, strengths, fit_score, job_description)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Changed from gpt-4 to gpt-3.5-turbo
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional recruiter reaching out to potential candidates on LinkedIn. Write personalized, professional, and engaging messages that reference specific details from their profile and explain why they're a great fit for the role. Keep messages under 200 words and maintain a warm, professional tone."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            message = response.choices[0].message.content.strip()
            
            # Clean up the message
            message = self._clean_message(message)
            
            return message
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_fallback_message(candidate, job_description)
    
    def _create_prompt(self, name: str, headline: str, strengths: List[str], 
                      fit_score: float, job_description: str) -> str:
        """Create a detailed prompt for message generation"""
        
        # Extract job details
        job_title = self._extract_job_title(job_description)
        company = self._extract_company(job_description)
        
        prompt = f"""
Generate a personalized LinkedIn outreach message for a candidate with the following details:

Candidate Name: {name}
Professional Headline: {headline}
Fit Score: {fit_score}/10
Key Strengths: {', '.join(strengths)}

Job Details:
Title: {job_title}
Company: {company}
Description: {job_description[:500]}...

Requirements:
1. Start with a personalized greeting using their name
2. Reference specific details from their headline/background
3. Mention their key strengths that align with the role
4. Explain why they're a great fit for this specific position
5. Include a clear call-to-action (e.g., "Would you be interested in learning more?")
6. Keep it professional but warm
7. Stay under 200 words
8. Don't be overly salesy or pushy

Generate the message:
"""
        return prompt
    
    def _extract_strengths(self, score_breakdown: Dict) -> List[str]:
        """Extract key strengths from score breakdown"""
        strengths = []
        
        if not score_breakdown:
            return ["strong technical background"]
        
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
        
        return strengths if strengths else ["strong technical background"]
    
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
    
    def _extract_company(self, job_description: str) -> str:
        """Extract company name from description"""
        import re
        
        # Look for "at Company" pattern
        match = re.search(r'at\s+([A-Z][a-zA-Z\s]+?)(?:\s+in|\s+at|\s*$)', job_description)
        if match:
            return match.group(1).strip()
        
        # Look for company keywords
        company_keywords = ['Windsurf', 'Codeium', 'Google', 'Meta', 'Microsoft', 'Apple']
        for keyword in company_keywords:
            if keyword.lower() in job_description.lower():
                return keyword
        
        return "our company"
    
    def _clean_message(self, message: str) -> str:
        """Clean and format the generated message"""
        # Remove quotes if present
        if message.startswith('"') and message.endswith('"'):
            message = message[1:-1]
        
        # Remove extra whitespace
        message = ' '.join(message.split())
        
        # Ensure proper capitalization
        if message and not message[0].isupper():
            message = message[0].upper() + message[1:]
        
        return message
    
    def _generate_fallback_message(self, candidate: Dict, job_description: str) -> str:
        """Generate a fallback message if OpenAI fails"""
        name = candidate.get('name', 'there')
        headline = candidate.get('headline', '')
        job_title = self._extract_job_title(job_description)
        company = self._extract_company(job_description)
        fit_score = candidate.get('fit_score', 0)
        
        # Extract first name
        first_name = name.split()[0] if name and ' ' in name else name
        
        # Create a more personalized fallback message
        if fit_score >= 8.0:
            quality = "excellent"
            enthusiasm = "very excited"
        elif fit_score >= 7.0:
            quality = "strong"
            enthusiasm = "excited"
        elif fit_score >= 6.0:
            quality = "good"
            enthusiasm = "interested"
        else:
            quality = "solid"
            enthusiasm = "interested"
        
        # Extract key skills from headline
        skills = []
        headline_lower = (headline or '').lower()
        if 'react' in headline_lower or 'javascript' in headline_lower:
            skills.append("frontend development")
        if 'python' in headline_lower or 'java' in headline_lower:
            skills.append("programming")
        if 'aws' in headline_lower or 'cloud' in headline_lower:
            skills.append("cloud technologies")
        if 'data' in headline_lower or 'ml' in headline_lower:
            skills.append("data science")
        if 'devops' in headline_lower or 'kubernetes' in headline_lower:
            skills.append("DevOps")
        
        skill_mention = f"your experience in {', '.join(skills)}" if skills else "your technical background"
        
        message = f"""Hi {first_name},

I came across your profile and was impressed by {skill_mention}. Your background in {headline[:100]}... caught my attention.

I'm reaching out because I think you'd be a {quality} fit for a {job_title} role at {company}. Your experience and skills align perfectly with what we're looking for, and I'm {enthusiasm} about the possibility of working together.

Would you be interested in learning more about this opportunity? I'd love to discuss how your background could contribute to our team and share more details about the role.

Best regards,
[Your Name]"""
        
        return message 