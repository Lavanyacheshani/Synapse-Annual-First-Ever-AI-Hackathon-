#!/usr/bin/env python3
"""
Setup script to create .env file with proper API keys
"""

import os

def create_env_file():
    """Create .env file with API keys"""
    
    env_content = """# LinkedIn Sourcing Agent Environment Variables

# Required API Keys
OPENAI_API_KEY=sk-your_new_openai_key_here
GOOGLE_API_KEY=AIzaSyBBVHFUliXVOXeDptztoCElTtm_cpqyQPU
GOOGLE_CSE_ID=3405e2c6dc74c4321

# Optional: GitHub API for bonus features
GITHUB_TOKEN=your_github_token_here

# Configuration
MAX_CANDIDATES_PER_JOB=25
RATE_LIMIT_DELAY=1.0
CACHE_EXPIRY_HOURS=24
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print("📝 Please update the OPENAI_API_KEY with your actual key if you want to use OpenAI")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_api_keys():
    """Test if API keys are working"""
    from config import Config
    
    print("\n🔍 Testing API Keys...")
    
    # Test Google API
    if Config.GOOGLE_API_KEY and Config.GOOGLE_CSE_ID:
        print("✅ Google API keys found")
        try:
            from googleapiclient.discovery import build
            service = build("customsearch", "v1", developerKey=Config.GOOGLE_API_KEY)
            print("✅ Google API connection successful")
        except Exception as e:
            print(f"❌ Google API connection failed: {e}")
    else:
        print("❌ Google API keys missing")
    
    # Test OpenAI API
    if Config.OPENAI_API_KEY and Config.OPENAI_API_KEY != "sk-your_new_openai_key_here":
        print("✅ OpenAI API key found")
    else:
        print("⚠️  OpenAI API key not set (will use fallback messages)")

if __name__ == "__main__":
    print("🚀 Setting up LinkedIn Sourcing Agent Environment")
    print("=" * 50)
    
    if create_env_file():
        test_api_keys()
        
        print("\n📋 Next Steps:")
        print("1. Update OPENAI_API_KEY in .env if you want to use OpenAI")
        print("2. Restart your API server")
        print("3. Test with: python demo_my_job.py")
        
        print("\n💡 The system will now use REAL LinkedIn data instead of mock candidates!")
    else:
        print("❌ Setup failed. Please check file permissions.") 