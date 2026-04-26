# Instagram Content Analysis & AI Suggestion System

Production-style Flask app that analyzes Instagram reels, performs NLP insights, computes retention, and generates AI improvement suggestions.

## Features
- Instagram reel URL input
- Free hybrid scraping:
  - Instaloader (best with login/session)
  - Playwright fallback for public pages
  - Demo fallback if Instagram blocks access
- Keyword extraction from caption/title
- Retention score and level classification
- Dynamic rule-based suggestion engine
- Dashboard + analysis history
- JSON storage (`analysis_history.json`)
- Auto demo-data fallback when scraping fails/private post/API issues

## Run
1. Install dependencies:
   - `pip install -r requirements.txt`
2. Install Playwright browser (one-time):
   - `python -m playwright install chromium`
3. (Recommended) Set Instagram login for maximum reliability:
   - `INSTA_USERNAME=your_username`
   - `INSTA_PASSWORD=your_password`
   - Optional: `INSTA_SESSION_FILE=insta_session` (default)
4. Start:
   - `python app.py`
5. Open:
   - `http://127.0.0.1:5000/`

## Project Structure
- `app.py` Flask routes (`/`, `/analyze`, `/history`)
- `scraper/instagram_scraper.py` scraper + normalization + fallback
- `analysis/keyword_extraction.py`
- `analysis/retention_analysis.py`
- `analysis/suggestion_engine.py`
- `database.py` JSON storage helpers
- `templates/` UI templates
- `static/style.css` and `static/main.js`
