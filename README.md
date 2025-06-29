
# Synapse AI: LinkedIn Candidate Sourcing Agent

## Overview

This project is an AI-powered LinkedIn candidate sourcing, scoring, and outreach generation tool. It uses Google Custom Search, OpenAI, and optional multi-source data (GitHub, Twitter, etc.) to find and rank candidates for a given job description.

---

## 🗂️ Project Structure

```mermaid
graph TD;
    A[User/API Request] --> B[FastAPI Server]
    B --> C[LinkedInAgent (agent/__init__.py)]
    C --> D1[LinkedInSearcher]
    C --> D2[CandidateScorer]
    C --> D3[OutreachGenerator]
    C --> D4[CacheManager]
    C --> D5[MultiSourceEnhancer]
    D1 --> E1[Google Custom Search]
    D3 --> E2[OpenAI API]
    D5 --> E3[GitHub/Twitter/StackOverflow]
    B --> F[data/ (cache, results)]
```

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd synapse_AI
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root with the following keys:

```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
OPENAI_API_KEY=sk-...              # Optional, for AI-powered outreach
GITHUB_TOKEN=ghp_...               # Optional, for GitHub enhancement
TWITTER_BEARER_TOKEN=...           # Optional, for Twitter enhancement
ENABLE_TWITTER_API=false           # Set to true to enable Twitter enrichment
```

Get Google API keys from: https://console.developers.google.com/

Get OpenAI API keys from: https://platform.openai.com/account/api-keys

### 4. Test Your Environment

```bash
python setup_env.py
```

This script checks your API keys and reports any missing or invalid ones.

---

## ▶️ Running the Application

### 1. Start the API Server

```bash
python main.py
```

The server runs at: http://0.0.0.0:8000

If you see Agent not ready, recheck your .env file and restart the server.

### 2. Run the Demo Script

```bash
python demo_my_job.py
```

Follow prompts to enter a job description and view candidate results.

### 3. Run the Test Suite

```bash
python test_api_simple.py
python test_api_comprehensive.py
```

Or, using PowerShell:

```powershell
./test_api_powershell.ps1
```

---

## 🧩 Troubleshooting

- **Agent not ready:** Ensure your .env contains valid API keys. Restart the server afterward.
- **Port already in use:** Free up port 8000 or kill conflicting Python processes.
- **OpenAI API errors:** For `invalid_api_key`, double-check your OpenAI key or leave it blank to use fallback messaging.
- **Website/connection errors:** Some candidates may not have valid websites. These warnings are normal.

---

## 💡 Features

- LinkedIn candidate discovery using Google Custom Search API
- Multi-source enhancement (GitHub, Twitter, Stack Overflow, etc.)
- AI-powered personalized LinkedIn outreach generation
- Smart candidate scoring and ranking
- Batch job processing and caching

---

## 📋 API Endpoints

- **GET /**: Root endpoint that returns API metadata
- **GET /health**: Health check endpoint
- **POST /candidates**: Retrieves top candidates for a given job description
  - Input:
    ```json
    {
      "job_description": "string",
      "max_candidates": 10
    }
    ```
  - Output: Returns a JSON list of top candidates, scores, and AI-generated outreach messages.
- **POST /batch**: Processes multiple job descriptions in a single request
  - Input: Array of job descriptions
  - Output: Array of processed results
- **GET /stats**: Returns system usage and performance statistics

---

## 🧪 Usage Example (CLI)

```bash
curl -X POST "https://your-space.hf.space/candidates" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Senior Software Engineer with React and Python experience",
    "max_candidates": 10
  }'
```

---

## 📊 Sample Response Format

```json
{
  "job_description": "Senior Software Engineer...",
  "timestamp": "2024-01-01T12:00:00",
  "total_candidates_found": 25,
  "top_candidates": [
    {
      "name": "John Doe",
      "linkedin_url": "https://linkedin.com/in/johndoe",
      "headline": "Senior Software Engineer at Tech Corp",
      "fit_score": 8.5,
      "score_breakdown": {
        "education": 8.0,
        "trajectory": 9.0,
        "company": 8.5,
        "skills": 9.5,
        "location": 10.0,
        "tenure": 7.0
      },
      "outreach_message": "Hi John, I noticed your impressive React experience...",
      "key_characteristics": {
        "school": "MIT",
        "years_experience": 7
      },
      "job_matches": {
        "location_match": true,
        "skills_match": true
      }
    }
  ],
  "processing_time": 2.5
}
```

---

## ⚙️ Technical Details

- **Framework:** FastAPI
- **Language:** Python 3.9+
- **Deployment:** Hugging Face Spaces (Docker container)
- **Default Port:** 7860

---

## 🔐 Environment Variables (Hugging Face)

Add these in your Hugging Face Space → "Settings" → "Secrets":

```env
GOOGLE_API_KEY=your_key
GOOGLE_CSE_ID=your_cse_id
OPENAI_API_KEY=your_openai_key  # Optional
```

---

## 🪪 License

This project is licensed under the MIT License.
See the LICENSE file for full details.

Built with ❤️ for AI-powered recruiting
