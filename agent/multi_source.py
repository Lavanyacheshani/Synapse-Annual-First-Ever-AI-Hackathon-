import re
import time
import requests
import json
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, urljoin
from config import Config

def safe_split_lower(val, idx):
    val = (val or '').strip()
    parts = val.split()
    if len(parts) > idx:
        return parts[idx].lower()
    return ''

class MultiSourceEnhancer:
    """Enhanced multi-source data collection for candidate profiles"""
    
    def __init__(self):
        self.github_token = Config.GITHUB_TOKEN
        self.twitter_bearer_token = Config.TWITTER_BEARER_TOKEN if Config.ENABLE_TWITTER_API else None
        self.session = requests.Session()
        
        # Set up GitHub API headers
        if self.github_token:
            self.session.headers.update({
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        
        # Log available APIs
        print(f"🔗 Multi-source enhancement initialized:")
        print(f"   - GitHub API: {'✅' if self.github_token else '❌'}")
        print(f"   - Twitter API: {'✅' if self.twitter_bearer_token else '❌'}")
        print(f"   - Website Analysis: ✅")
        print(f"   - Stack Overflow: {'✅' if self.github_token else '❌'}")
        print(f"   - Medium: ✅")
    
    def enhance_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """Enhance all candidates with comprehensive multi-source data"""
        enhanced_candidates = []
        
        for i, candidate in enumerate(candidates):
            try:
                print(f"🔍 Enhancing candidate {i+1}/{len(candidates)}: {candidate.get('name', 'Unknown')}")
                enhanced_candidate = self.enhance_candidate(candidate)
                enhanced_candidates.append(enhanced_candidate)
                
                # Rate limiting to be respectful to APIs
                time.sleep(1.0)
                
            except Exception as e:
                print(f"❌ Error enhancing candidate {candidate.get('name', 'Unknown')}: {e}")
                enhanced_candidates.append(candidate)
        
        return enhanced_candidates
    
    def enhance_candidate(self, candidate: Dict) -> Dict:
        """Enhance a single candidate with comprehensive multi-source data"""
        enhanced = candidate.copy()
        
        # Extract candidate information
        linkedin_username = candidate.get('linkedin_username', '')
        name = candidate.get('name', '')
        headline = candidate.get('headline', '')
        
        # Collect data from multiple sources
        sources_data = {}
        
        # 1. GitHub Profile (most important for tech roles)
        github_data = self._find_github_profile(name, linkedin_username, headline)
        if github_data:
            sources_data['github'] = github_data
            enhanced['github_score'] = self._calculate_github_score(github_data)
        
        # 2. Personal Website
        website_data = self._find_personal_website(name, linkedin_username, headline)
        if website_data:
            sources_data['website'] = website_data
            enhanced['website_score'] = self._calculate_website_score(website_data)
        
        # 3. Stack Overflow Profile
        stackoverflow_data = self._find_stackoverflow_profile(name, linkedin_username)
        if stackoverflow_data:
            sources_data['stackoverflow'] = stackoverflow_data
            enhanced['stackoverflow_score'] = self._calculate_stackoverflow_score(stackoverflow_data)
        
        # 4. Medium/Blog Posts
        medium_data = self._find_medium_profile(name, linkedin_username)
        if medium_data:
            sources_data['medium'] = medium_data
            enhanced['medium_score'] = self._calculate_medium_score(medium_data)
        
        # 5. Twitter Profile
        twitter_data = self._find_twitter_profile(name, linkedin_username)
        if twitter_data:
            sources_data['twitter'] = twitter_data
            enhanced['twitter_score'] = self._calculate_twitter_score(twitter_data)
        
        # 6. Additional professional platforms
        additional_data = self._find_additional_sources(name, linkedin_username, headline)
        if additional_data:
            sources_data['additional'] = additional_data
        
        # Store all source data
        enhanced['multi_source_data'] = sources_data
        
        # Calculate comprehensive enhancement score
        enhancement_score = self._calculate_comprehensive_enhancement_score(enhanced)
        enhanced['enhancement_score'] = enhancement_score
        
        # Add skills extracted from multi-source data
        enhanced['extracted_skills'] = self._extract_skills_from_sources(sources_data)
        
        return enhanced
    
    def _find_github_profile(self, name: str, linkedin_username: str, headline: str) -> Optional[Dict]:
        """Find and analyze GitHub profile for a candidate"""
        if not self.github_token:
            return None
        
        # Try different search strategies
        search_queries = [
            name,
            linkedin_username,
            (safe_split_lower(name, 0) + ' ' + safe_split_lower(name, -1)) if ' ' in (name or '') else '',
            (safe_split_lower(name, 0) + ' ' + safe_split_lower(name, -1)) if ' ' in (name or '') else '',
            # Try variations based on headline
            safe_split_lower(name, 0) if ' ' in (name or '') else name,
        ]
        
        for query in search_queries:
            try:
                # Search GitHub users
                response = self.session.get(
                    'https://api.github.com/search/users',
                    params={'q': query, 'per_page': 10}
                )
                
                if response.status_code == 200:
                    users = response.json().get('items', [])
                    
                    for user in users:
                        # Get detailed user info
                        user_response = self.session.get(user['url'])
                        if user_response.status_code == 200:
                            user_data = user_response.json()
                            
                            # Get repositories
                            repos_response = self.session.get(
                                user_data['repos_url'],
                                params={'sort': 'stars', 'per_page': 10}
                            )
                            
                            if repos_response.status_code == 200:
                                repos = repos_response.json()
                                
                                # Get contribution data
                                contribution_data = self._get_github_contributions(user_data['login'])
                                
                                return {
                                    'username': user_data['login'],
                                    'name': user_data.get('name', ''),
                                    'bio': user_data.get('bio', ''),
                                    'location': user_data.get('location', ''),
                                    'company': user_data.get('company', ''),
                                    'public_repos': user_data.get('public_repos', 0),
                                    'followers': user_data.get('followers', 0),
                                    'following': user_data.get('following', 0),
                                    'created_at': user_data.get('created_at', ''),
                                    'updated_at': user_data.get('updated_at', ''),
                                    'top_repos': [
                                        {
                                            'name': repo['name'],
                                            'description': repo.get('description', ''),
                                            'language': repo.get('language', ''),
                                            'stars': repo.get('stargazers_count', 0),
                                            'forks': repo.get('forks_count', 0),
                                            'size': repo.get('size', 0),
                                            'updated_at': repo.get('updated_at', ''),
                                            'topics': repo.get('topics', [])
                                        }
                                        for repo in repos[:5]
                                    ],
                                    'languages_used': self._extract_languages_from_repos(repos),
                                    'contribution_data': contribution_data,
                                    'profile_completeness': self._calculate_profile_completeness(user_data)
                                }
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"Error searching GitHub for {query}: {e}")
                continue
        
        return None
    
    def _get_github_contributions(self, username: str) -> Dict:
        """Get GitHub contribution data (simulated for now)"""
        # In a real implementation, you'd scrape the contribution graph
        # or use GitHub's GraphQL API
        return {
            'total_contributions': 0,
            'streak_days': 0,
            'longest_streak': 0,
            'contribution_years': 0
        }
    
    def _extract_languages_from_repos(self, repos: List[Dict]) -> Dict[str, int]:
        """Extract programming languages from repositories"""
        languages = {}
        for repo in repos:
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        return languages
    
    def _calculate_profile_completeness(self, user_data: Dict) -> float:
        """Calculate GitHub profile completeness score"""
        fields = ['name', 'bio', 'location', 'company', 'blog']
        completed = sum(1 for field in fields if user_data.get(field))
        return completed / len(fields)
    
    def _find_personal_website(self, name: str, linkedin_username: str, headline: str) -> Optional[Dict]:
        """Find and analyze personal website for a candidate"""
        # Try common patterns for personal websites
        potential_domains = [
            f"https://{linkedin_username}.com",
            f"https://{(safe_split_lower(name, 0) + safe_split_lower(name, -1)) if ' ' in (name or '') else ''}.com",
            f"https://{(safe_split_lower(name, 0)) if ' ' in (name or '') else ''}{(safe_split_lower(name, -1)) if ' ' in (name or '') else ''}.com",
            f"https://{(safe_split_lower(name, 0)) if ' ' in (name or '') else ''}.com",
            f"https://{(safe_split_lower(name, -1)) if ' ' in (name or '') else ''}.com"
        ]
        
        for domain in potential_domains:
            try:
                response = requests.get(domain, timeout=10, headers={'User-Agent': 'LinkedIn-Sourcing-Agent/1.0'})
                if response.status_code == 200:
                    content = response.text
                    return {
                        'url': domain,
                        'title': self._extract_title(content),
                        'description': self._extract_description(content),
                        'accessible': True,
                        'content_length': len(content),
                        'has_blog': 'blog' in (content or '').lower() or 'posts' in (content or '').lower(),
                        'has_portfolio': any(word in (content or '').lower() for word in ['portfolio', 'projects', 'work']),
                        'has_contact': any(word in (content or '').lower() for word in ['contact', 'email', 'phone']),
                        'technologies_mentioned': self._extract_technologies_from_website(content)
                    }
            except Exception as e:
                print(f"Error checking website {domain}: {e}")
                continue
        
        return None
    
    def _find_stackoverflow_profile(self, name: str, linkedin_username: str) -> Optional[Dict]:
        """Find Stack Overflow profile using Stack Exchange API"""
        try:
            # Try different potential usernames
            potential_handles = [
                linkedin_username,
                (safe_split_lower(name, 0) + safe_split_lower(name, -1)) if ' ' in (name or '') else '',
                (safe_split_lower(name, 0) + safe_split_lower(name, -1)) if ' ' in (name or '') else '',
            ]
            
            for handle in potential_handles:
                try:
                    # Search for user on Stack Overflow
                    user_data = self._get_stackoverflow_user(handle)
                    if user_data:
                        return user_data
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error searching Stack Overflow for {handle}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error in Stack Overflow profile search: {e}")
            return self._get_simulated_stackoverflow_data(name, linkedin_username)
    
    def _get_stackoverflow_user(self, username: str) -> Optional[Dict]:
        """Get Stack Overflow user data using Stack Exchange API"""
        try:
            # Stack Exchange API endpoint
            url = "https://api.stackexchange.com/2.3/users"
            params = {
                'inname': username,
                'site': 'stackoverflow',
                'pagesize': 5,
                'order': 'desc',
                'sort': 'reputation'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('items', [])
                
                if users:
                    user = users[0]  # Get the most relevant user
                    
                    # Get user's top tags
                    tags_data = self._get_user_top_tags(user.get('user_id'))
                    
                    # Get user's badges
                    badges_data = self._get_user_badges(user.get('user_id'))
                    
                    return {
                        'username': user.get('display_name', ''),
                        'display_name': user.get('display_name', ''),
                        'reputation': user.get('reputation', 0),
                        'answers': user.get('answer_count', 0),
                        'questions': user.get('question_count', 0),
                        'badges': badges_data.get('badges', []),
                        'top_tags': tags_data.get('tags', []),
                        'member_since': user.get('creation_date', ''),
                        'last_seen': user.get('last_access_date', ''),
                        'profile_image': user.get('profile_image', ''),
                        'location': user.get('location', ''),
                        'website_url': user.get('website_url', ''),
                        'about_me': user.get('about_me', ''),
                        'accept_rate': user.get('accept_rate', 0)
                    }
            
            return None
            
        except Exception as e:
            print(f"Error getting Stack Overflow user {username}: {e}")
            return None
    
    def _get_user_top_tags(self, user_id: int) -> Dict:
        """Get user's top tags from Stack Overflow"""
        if not user_id:
            return {'tags': []}
        
        try:
            url = f"https://api.stackexchange.com/2.3/users/{user_id}/top-tags"
            params = {
                'site': 'stackoverflow',
                'pagesize': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tags = data.get('items', [])
                
                return {
                    'tags': [
                        {
                            'tag_name': tag.get('tag_name', ''),
                            'answer_count': tag.get('answer_count', 0),
                            'question_count': tag.get('question_count', 0),
                            'score': tag.get('score', 0)
                        }
                        for tag in tags
                    ]
                }
            
            return {'tags': []}
            
        except Exception as e:
            print(f"Error getting user top tags: {e}")
            return {'tags': []}
    
    def _get_user_badges(self, user_id: int) -> Dict:
        """Get user's badges from Stack Overflow"""
        if not user_id:
            return {'badges': []}
        
        try:
            url = f"https://api.stackexchange.com/2.3/users/{user_id}/badges"
            params = {
                'site': 'stackoverflow',
                'pagesize': 20,
                'order': 'desc',
                'sort': 'rank'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                badges = data.get('items', [])
                
                return {
                    'badges': [
                        {
                            'name': badge.get('name', ''),
                            'description': badge.get('description', ''),
                            'rank': badge.get('rank', ''),
                            'award_count': badge.get('award_count', 0)
                        }
                        for badge in badges
                    ]
                }
            
            return {'badges': []}
            
        except Exception as e:
            print(f"Error getting user badges: {e}")
            return {'badges': []}
    
    def _get_simulated_stackoverflow_data(self, name: str, linkedin_username: str) -> Dict:
        """Get simulated Stack Overflow data when API is not available"""
        potential_handles = [
            linkedin_username,
            (safe_split_lower(name, 0) + safe_split_lower(name, -1)) if ' ' in (name or '') else '',
            (safe_split_lower(name, 0) + safe_split_lower(name, -1)) if ' ' in (name or '') else '',
        ]
        
        return {
            'username': potential_handles[0],
            'display_name': name,
            'reputation': 0,  # Would be real data from Stack Overflow API
            'answers': 0,
            'questions': 0,
            'badges': [],
            'top_tags': [],
            'member_since': '',
            'last_seen': '',
            'profile_image': '',
            'location': '',
            'website_url': '',
            'about_me': '',
            'accept_rate': 0
        }
    
    def _find_medium_profile(self, name: str, linkedin_username: str) -> Optional[Dict]:
        """Find Medium profile and articles (simulated)"""
        # Medium doesn't have a public API, so we'll simulate this
        # In a real implementation, you'd scrape their website
        
        return {
            'username': linkedin_username,
            'display_name': name,
            'followers': 0,
            'articles_count': 0,
            'top_articles': [],
            'member_since': ''
        }
    
    def _find_twitter_profile(self, name: str, linkedin_username: str) -> Optional[Dict]:
        """Find Twitter profile using Twitter API v2"""
        # Check if Twitter API credentials are available
        if not hasattr(self, 'twitter_bearer_token') or not self.twitter_bearer_token:
            print("Twitter API not configured - using simulated data")
            return self._get_simulated_twitter_data(name, linkedin_username)
        
        try:
            # Try different potential usernames
            potential_handles = [
                linkedin_username,
                (safe_split_lower(name, 0) + safe_split_lower(name, -1)) if ' ' in (name or '') else '',
                (safe_split_lower(name, 0) + safe_split_lower(name, -1)) if ' ' in (name or '') else '',
            ]
            
            for handle in potential_handles:
                try:
                    # Search for user by username
                    user_data = self._get_twitter_user_by_username(handle)
                    if user_data:
                        return user_data
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error searching Twitter for {handle}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error in Twitter profile search: {e}")
            return self._get_simulated_twitter_data(name, linkedin_username)
    
    def _get_twitter_user_by_username(self, username: str) -> Optional[Dict]:
        """Get Twitter user data by username using API v2"""
        try:
            headers = {
                'Authorization': f'Bearer {self.twitter_bearer_token}',
                'Content-Type': 'application/json'
            }
            
            # Get user by username
            url = f"https://api.twitter.com/2/users/by/username/{username}"
            params = {
                'user.fields': 'id,username,name,description,location,verified,public_metrics,created_at,profile_image_url'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json().get('data', {})
                
                # Get recent tweets for additional analysis
                tweets_data = self._get_recent_tweets(user_data.get('id'))
                
                return {
                    'username': user_data.get('username', ''),
                    'display_name': user_data.get('name', ''),
                    'followers_count': user_data.get('public_metrics', {}).get('followers_count', 0),
                    'following_count': user_data.get('public_metrics', {}).get('following_count', 0),
                    'tweet_count': user_data.get('public_metrics', {}).get('tweet_count', 0),
                    'verified': user_data.get('verified', False),
                    'bio': user_data.get('description', ''),
                    'location': user_data.get('location', ''),
                    'created_at': user_data.get('created_at', ''),
                    'profile_image_url': user_data.get('profile_image_url', ''),
                    'recent_tweets': tweets_data.get('tweets', []),
                    'engagement_rate': self._calculate_twitter_engagement_rate(user_data.get('public_metrics', {}))
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting Twitter user {username}: {e}")
            return None
    
    def _get_recent_tweets(self, user_id: str) -> Dict:
        """Get recent tweets for a user"""
        if not user_id:
            return {'tweets': []}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.twitter_bearer_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"https://api.twitter.com/2/users/{user_id}/tweets"
            params = {
                'max_results': 10,
                'tweet.fields': 'created_at,public_metrics,entities'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                tweets_data = response.json()
                tweets = tweets_data.get('data', [])
                
                return {
                    'tweets': [
                        {
                            'id': tweet.get('id'),
                            'text': tweet.get('text', ''),
                            'created_at': tweet.get('created_at'),
                            'likes': tweet.get('public_metrics', {}).get('like_count', 0),
                            'retweets': tweet.get('public_metrics', {}).get('retweet_count', 0),
                            'replies': tweet.get('public_metrics', {}).get('reply_count', 0)
                        }
                        for tweet in tweets
                    ]
                }
            
            return {'tweets': []}
            
        except Exception as e:
            print(f"Error getting recent tweets: {e}")
            return {'tweets': []}
    
    def _calculate_twitter_engagement_rate(self, metrics: Dict) -> float:
        """Calculate Twitter engagement rate"""
        followers = metrics.get('followers_count', 1)
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        
        total_engagement = likes + retweets + replies
        engagement_rate = (total_engagement / followers) * 100 if followers > 0 else 0
        
        return round(engagement_rate, 2)
    
    def _get_simulated_twitter_data(self, name: str, linkedin_username: str) -> Dict:
        """Get simulated Twitter data when API is not available"""
        potential_handles = [
            linkedin_username,
            (safe_split_lower(name, 0) + safe_split_lower(name, -1)) if ' ' in (name or '') else '',
            (safe_split_lower(name, 0) + safe_split_lower(name, -1)) if ' ' in (name or '') else '',
        ]
        
        return {
            'username': potential_handles[0],
            'display_name': name,
            'followers_count': 0,  # Would be real data from Twitter API
            'following_count': 0,
            'tweet_count': 0,
            'verified': False,
            'bio': '',
            'location': '',
            'created_at': '',
            'profile_image_url': '',
            'recent_tweets': [],
            'engagement_rate': 0.0
        }
    
    def _find_additional_sources(self, name: str, linkedin_username: str, headline: str) -> Optional[Dict]:
        """Find additional professional sources"""
        additional_sources = {}
        
        # Try to find other professional platforms
        # This could include: Dribbble, Behance, Dev.to, Hashnode, etc.
        
        return additional_sources if additional_sources else None
    
    def _calculate_github_score(self, github_data: Dict) -> float:
        """Calculate comprehensive GitHub score"""
        if not github_data:
            return 0.0
        
        score = 0.0
        
        # Profile completeness (10% of total)
        completeness = github_data.get('profile_completeness', 0.0)
        score += completeness * 1.0
        
        # Followers (20% of total)
        followers = github_data.get('followers', 0)
        if followers >= 1000:
            score += 2.0
        elif followers >= 500:
            score += 1.5
        elif followers >= 100:
            score += 1.0
        elif followers >= 50:
            score += 0.5
        
        # Public repositories (15% of total)
        repos = github_data.get('public_repos', 0)
        if repos >= 50:
            score += 1.5
        elif repos >= 20:
            score += 1.0
        elif repos >= 10:
            score += 0.5
        
        # Repository quality (25% of total)
        top_repos = github_data.get('top_repos', [])
        total_stars = sum(repo.get('stars', 0) for repo in top_repos)
        total_forks = sum(repo.get('forks', 0) for repo in top_repos)
        
        if total_stars >= 1000:
            score += 2.5
        elif total_stars >= 500:
            score += 2.0
        elif total_stars >= 100:
            score += 1.5
        elif total_stars >= 50:
            score += 1.0
        
        # Language diversity (10% of total)
        languages = github_data.get('languages_used', {})
        if len(languages) >= 5:
            score += 1.0
        elif len(languages) >= 3:
            score += 0.7
        elif len(languages) >= 2:
            score += 0.5
        
        # Account age and activity (20% of total)
        created_at = github_data.get('created_at', '')
        if created_at:
            import datetime
            try:
                created_date = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                age_years = (datetime.datetime.now(datetime.timezone.utc) - created_date).days / 365
                
                if age_years >= 5:
                    score += 2.0
                elif age_years >= 3:
                    score += 1.5
                elif age_years >= 1:
                    score += 1.0
            except:
                pass
        
        return min(score, 10.0)  # Cap at 10
    
    def _calculate_website_score(self, website_data: Dict) -> float:
        """Calculate website quality score"""
        if not website_data:
            return 0.0
        
        score = 0.0
        
        # Basic accessibility
        if website_data.get('accessible', False):
            score += 1.0
        
        # Content quality
        content_length = website_data.get('content_length', 0)
        if content_length >= 10000:
            score += 2.0
        elif content_length >= 5000:
            score += 1.5
        elif content_length >= 1000:
            score += 1.0
        
        # Professional features
        if website_data.get('has_blog', False):
            score += 1.5
        if website_data.get('has_portfolio', False):
            score += 1.5
        if website_data.get('has_contact', False):
            score += 0.5
        
        # Technology mentions
        tech_count = len(website_data.get('technologies_mentioned', []))
        if tech_count >= 5:
            score += 1.0
        elif tech_count >= 3:
            score += 0.7
        elif tech_count >= 1:
            score += 0.3
        
        return min(score, 10.0)
    
    def _calculate_stackoverflow_score(self, stackoverflow_data: Dict) -> float:
        """Calculate Stack Overflow score"""
        if not stackoverflow_data:
            return 0.0
        
        score = 0.0
        
        # Reputation
        reputation = stackoverflow_data.get('reputation', 0)
        if reputation >= 10000:
            score += 3.0
        elif reputation >= 5000:
            score += 2.0
        elif reputation >= 1000:
            score += 1.0
        
        # Answers
        answers = stackoverflow_data.get('answers', 0)
        if answers >= 100:
            score += 2.0
        elif answers >= 50:
            score += 1.5
        elif answers >= 10:
            score += 1.0
        
        # Badges
        badges = stackoverflow_data.get('badges', [])
        if len(badges) >= 10:
            score += 2.0
        elif len(badges) >= 5:
            score += 1.5
        elif len(badges) >= 1:
            score += 1.0
        
        return min(score, 10.0)
    
    def _calculate_medium_score(self, medium_data: Dict) -> float:
        """Calculate Medium score"""
        if not medium_data:
            return 0.0
        
        score = 0.0
        
        # Followers
        followers = medium_data.get('followers', 0)
        if followers >= 1000:
            score += 3.0
        elif followers >= 500:
            score += 2.0
        elif followers >= 100:
            score += 1.0
        
        # Articles
        articles = medium_data.get('articles_count', 0)
        if articles >= 20:
            score += 3.0
        elif articles >= 10:
            score += 2.0
        elif articles >= 5:
            score += 1.0
        
        return min(score, 10.0)
    
    def _calculate_twitter_score(self, twitter_data: Dict) -> float:
        """Calculate Twitter score"""
        if not twitter_data:
            return 0.0
        
        score = 0.0
        
        # Followers
        followers = twitter_data.get('followers_count', 0)
        if followers >= 10000:
            score += 3.0
        elif followers >= 5000:
            score += 2.0
        elif followers >= 1000:
            score += 1.0
        
        # Tweet count
        tweets = twitter_data.get('tweet_count', 0)
        if tweets >= 1000:
            score += 2.0
        elif tweets >= 500:
            score += 1.5
        elif tweets >= 100:
            score += 1.0
        
        # Verification
        if twitter_data.get('verified', False):
            score += 1.0
        
        return min(score, 10.0)
    
    def _calculate_comprehensive_enhancement_score(self, candidate: Dict) -> float:
        """Calculate overall enhancement score with weighted contributions"""
        score = 0.0
        total_weight = 0.0
        
        # GitHub (most important for tech roles) - 40% weight
        github_score = candidate.get('github_score', 0.0)
        score += github_score * 0.4
        total_weight += 0.4
        
        # Website (professional presence) - 25% weight
        website_score = candidate.get('website_score', 0.0)
        score += website_score * 0.25
        total_weight += 0.25
        
        # Stack Overflow (technical expertise) - 20% weight
        stackoverflow_score = candidate.get('stackoverflow_score', 0.0)
        score += stackoverflow_score * 0.2
        total_weight += 0.2
        
        # Medium (thought leadership) - 10% weight
        medium_score = candidate.get('medium_score', 0.0)
        score += medium_score * 0.1
        total_weight += 0.1
        
        # Twitter (social presence) - 5% weight
        twitter_score = candidate.get('twitter_score', 0.0)
        score += twitter_score * 0.05
        total_weight += 0.05
        
        # Normalize by total weight
        if total_weight > 0:
            score = score / total_weight
        
        return round(score, 2)
    
    def _extract_skills_from_sources(self, sources_data: Dict) -> List[str]:
        """Extract skills from all multi-source data"""
        skills = set()
        
        # Extract from GitHub
        if 'github' in sources_data:
            github_data = sources_data['github']
            
            # Languages from repositories
            languages = github_data.get('languages_used', {})
            skills.update(languages.keys())
            
            # Topics from repositories
            for repo in github_data.get('top_repos', []):
                skills.update(repo.get('topics', []))
        
        # Extract from website
        if 'website' in sources_data:
            website_data = sources_data['website']
            skills.update(website_data.get('technologies_mentioned', []))
        
        # Extract from Stack Overflow
        if 'stackoverflow' in sources_data:
            stackoverflow_data = sources_data['stackoverflow']
            skills.update(stackoverflow_data.get('top_tags', []))
        
        return list(skills)
    
    def _extract_title(self, html_content: str) -> str:
        """Extract title from HTML content"""
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        return ""
    
    def _extract_description(self, html_content: str) -> str:
        """Extract meta description from HTML content"""
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        if desc_match:
            return desc_match.group(1).strip()
        return ""
    
    def _extract_technologies_from_website(self, html_content: str) -> List[str]:
        """Extract mentioned technologies from website content"""
        # Common technology keywords
        tech_keywords = [
            'react', 'angular', 'vue', 'node.js', 'python', 'java', 'javascript',
            'typescript', 'php', 'ruby', 'go', 'rust', 'c++', 'c#', 'swift',
            'kotlin', 'scala', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'machine learning', 'ai', 'data science', 'blockchain'
        ]
        
        content_lower = html_content.lower()
        found_technologies = []
        
        for tech in tech_keywords:
            if tech in content_lower:
                found_technologies.append(tech)
        
        return found_technologies 