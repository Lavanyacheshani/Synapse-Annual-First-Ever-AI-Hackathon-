#!/usr/bin/env python3
"""
Test script to verify API keys and test system components
"""

import os
import sys
from dotenv import load_dotenv

def test_env_file():
    """Test if .env file exists and has required keys"""
    print("🔍 Testing environment setup...")
    
    # Load environment variables
    load_dotenv()
    
    required_keys = ['OPENAI_API_KEY', 'GOOGLE_API_KEY', 'GOOGLE_CSE_ID']
    missing_keys = []
    
    for key in required_keys:
        value = os.getenv(key)
        if not value or value == f'your_{key.lower()}_here':
            missing_keys.append(key)
        else:
            print(f"✅ {key}: {'*' * (len(value) - 8) + value[-8:] if len(value) > 8 else '*' * len(value)}")
    
    if missing_keys:
        print(f"❌ Missing or invalid API keys: {', '.join(missing_keys)}")
        print("\n📝 Please create a .env file with the following format:")
        print("""
OPENAI_API_KEY=your_actual_openai_key_here
GOOGLE_API_KEY=your_actual_google_key_here
GOOGLE_CSE_ID=your_actual_cse_id_here
        """)
        return False
    
    print("✅ All required API keys are present!")
    return True

def test_google_api():
    """Test Google Custom Search API"""
    print("\n🔍 Testing Google Custom Search API...")
    
    try:
        from googleapiclient.discovery import build
        from config import Config
        
        # Test API key
        service = build("customsearch", "v1", developerKey=Config.GOOGLE_API_KEY)
        
        # Test a simple search
        try:
            results = service.cse().list(
                q="site:linkedin.com/in software engineer",
                cx=Config.GOOGLE_CSE_ID,
                num=1
            ).execute()
            
            if 'items' in results:
                print(f"✅ Google API working! Found {len(results['items'])} results")
                return True
            else:
                print("⚠️ Google API working but no results found (check CSE settings)")
                return True
                
        except Exception as e:
            print(f"❌ Google API search failed: {e}")
            print("💡 Make sure your Google Custom Search Engine is configured to search the entire web")
            return False
            
    except Exception as e:
        print(f"❌ Google API initialization failed: {e}")
        return False

def test_openai_api():
    """Test OpenAI API"""
    print("\n🔍 Testing OpenAI API...")
    
    try:
        import openai
        from config import Config
        
        openai.api_key = Config.OPENAI_API_KEY
        client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello World'"}],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ OpenAI API working!")
            return True
        else:
            print("❌ OpenAI API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_agent_components():
    """Test individual agent components"""
    print("\n🔍 Testing agent components...")
    
    try:
        from agent import LinkedInSourcingAgent
        
        # Initialize agent
        agent = LinkedInSourcingAgent()
        print("✅ Agent initialization successful")
        
        # Test search component
        try:
            candidates = agent.searcher.search("Software Engineer", max_candidates=3)
            print(f"✅ Search component working! Found {len(candidates)} candidates")
        except Exception as e:
            print(f"⚠️ Search component issue: {e}")
        
        # Test scoring component
        try:
            if candidates:
                scored = agent.scorer.score_all(candidates, "Software Engineer")
                print(f"✅ Scoring component working! Scored {len(scored)} candidates")
            else:
                print("⚠️ Skipping scoring test (no candidates)")
        except Exception as e:
            print(f"⚠️ Scoring component issue: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent component test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 LinkedIn Sourcing Agent - Setup Test")
    print("=" * 50)
    
    # Test environment
    env_ok = test_env_file()
    if not env_ok:
        sys.exit(1)
    
    # Test APIs
    google_ok = test_google_api()
    openai_ok = test_openai_api()
    
    # Test components
    agent_ok = test_agent_components()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 50)
    print(f"Environment Setup: {'✅' if env_ok else '❌'}")
    print(f"Google API: {'✅' if google_ok else '❌'}")
    print(f"OpenAI API: {'✅' if openai_ok else '❌'}")
    print(f"Agent Components: {'✅' if agent_ok else '❌'}")
    
    if all([env_ok, google_ok, openai_ok, agent_ok]):
        print("\n🎉 All tests passed! Your setup is ready to go!")
        print("\n🚀 You can now run:")
        print("   python run.py --job 'Software Engineer'")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
        print("\n💡 Common solutions:")
        print("   1. Make sure your .env file has valid API keys")
        print("   2. Check that your Google Custom Search Engine is configured")
        print("   3. Verify your OpenAI API key has credits")
        print("   4. Ensure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 