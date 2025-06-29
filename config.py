import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    
    # Configuration
    MAX_CANDIDATES_PER_JOB = int(os.getenv("MAX_CANDIDATES_PER_JOB", "25"))
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))
    CACHE_EXPIRY_HOURS = int(os.getenv("CACHE_EXPIRY_HOURS", "24"))
    
    # Feature flags
    USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() == "true"
    USE_FALLBACK_MESSAGES = os.getenv("USE_FALLBACK_MESSAGES", "false").lower() == "true"
    ENABLE_TWITTER_API = os.getenv("ENABLE_TWITTER_API", "false").lower() == "true"
    
    # Elite schools for scoring
    ELITE_SCHOOLS = {
        "MIT", "Stanford", "Harvard", "Berkeley", "CMU", "Caltech", 
        "Princeton", "Yale", "Columbia", "Cornell", "UCLA", "UCSD"
    }
    
    # Top tech companies for scoring
    TOP_TECH_COMPANIES = {
        "Google", "Meta", "Microsoft", "Apple", "Amazon", "Netflix",
        "Twitter", "LinkedIn", "Uber", "Airbnb", "Stripe", "Square",
        "Palantir", "Databricks", "Snowflake", "MongoDB", "Atlassian"
    }
    
    @classmethod
    def validate_keys(cls):
        """Validate that required API keys are present"""
        missing_keys = []
        if not cls.GOOGLE_API_KEY:
            missing_keys.append("GOOGLE_API_KEY")
        if not cls.GOOGLE_CSE_ID:
            missing_keys.append("GOOGLE_CSE_ID")
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
        
        return True 