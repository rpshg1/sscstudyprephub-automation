"""
Fetch and organize daily current affairs for SSC & Competitive exams.
Supports RSS feeds from Google News (India, World, Economy, Sports, Sci-Tech, States)
and optional Gemini API enhancement for exam-oriented static GK & MCQs.
"""

import os
import re
import datetime
import html
import feedparser
import requests

RSS_FEEDS = {
    "national": "https://news.google.com/rss/headlines/section/topic/NATION?hl=en-IN&gl=IN&ceid=IN:en",
    "international": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-IN&gl=IN&ceid=IN:en",
    "economy": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-IN&gl=IN&ceid=IN:en",
    "sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=en-IN&gl=IN&ceid=IN:en",
    "science_defence": "https://news.google.com/rss/search?q=ISRO+OR+DRDO+OR+military+exercise+OR+defence+India+when:2d&hl=en-IN&gl=IN&ceid=IN:en",
    "states_schemes": "https://news.google.com/rss/search?q=State+government+scheme+OR+Cabinet+approves+India+when:2d&hl=en-IN&gl=IN&ceid=IN:en",
    "appointments_awards": "https://news.google.com/rss/search?q=appointed+OR+takes+charge+OR+honoured+award+India+when:2d&hl=en-IN&gl=IN&ceid=IN:en",
}

def clean_text(raw_text):
    if not raw_text:
        return ""
    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", "", raw_text)
    clean = html.unescape(clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean

def clean_headline(title):
    # Google news titles often end with ' - Publisher'
    if " - " in title:
        parts = title.rsplit(" - ", 1)
        title = parts[0].strip()
    return clean_text(title)

def fetch_feed_items(url, limit=4):
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:limit]:
            title = clean_headline(entry.get("title", ""))
            summary = clean_text(entry.get("summary", ""))
            if summary.startswith(title):
                summary = summary[len(title):].strip()
            if not summary or len(summary) < 20:
                summary = "Key development covered in national media; critical for upcoming competitive exams."
            items.append({
                "title": title,
                "summary": summary,
                "link": entry.get("link", "")
            })
        return items
    except Exception as e:
        print(f"Error fetching feed {url}: {e}")
        return []

def get_gemini_enhanced_content(raw_topics, today_str, gemini_api_key):
    """
    If GEMINI_API_KEY is available, format news into high-yield SSC exam format
    with Static GK & 5 Daily Practice MCQs.
    """
    prompt = f"""
You are an expert Current Affairs content creator for Indian competitive exams (SSC CGL, CHSL, MTS, CPO, Banking, State PSCs).
Date: {today_str}

Here is today's raw news data across categories:
{raw_topics}

Format this into a structured JSON response with high-yield exam takeaways:
JSON structure:
{{
  "national": [
    {{
      "title": "Clean concise headline",
      "points": ["Fact 1 (What happened)", "Fact 2 (Key Ministry / Body involved)"],
      "exam_pointer": "Static GK takeaway (e.g. Minister name, headquarters, founding year)"
    }}
  ],
  "international": [
    {{
      "title": "Clean concise headline",
      "points": ["Fact 1", "Fact 2"],
      "exam_pointer": "Country Capital, Currency, President/PM"
    }}
  ],
  "states_schemes": [
    {{
      "title": "State/Scheme headline",
      "points": ["Objective & features"],
      "exam_pointer": "State Capital, Chief Minister, Governor"
    }}
  ],
  "economy": [
    {{
      "title": "Economy/Banking headline",
      "points": ["Key data points/policy"],
      "exam_pointer": "Headquarters, Governor/Chief, statutory body"
    }}
  ],
  "sports": [
    {{
      "title": "Sports headline",
      "points": ["Event, Winner, Venue"],
      "exam_pointer": "Associated trophy, governing body"
    }}
  ],
  "science_defence": [
    {{
      "title": "Science/Defence headline",
      "points": ["Satellite/Exercise details"],
      "exam_pointer": "Agency (ISRO/DRDO/Navy/Army), Chief, Location"
    }}
  ],
  "appointments_awards": [
    {{
      "title": "Person/Award headline",
      "points": ["Key designation / Award category"],
      "exam_pointer": "Tenure or predecessor details"
    }}
  ],
  "daily_quiz": [
    {{
      "question": "Question text...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "Correct Option with 1-line explanation"
    }}
  ]
}}

Return ONLY valid JSON without markdown fences.
"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        res = requests.post(url, json=payload, timeout=45)
        if res.status_code == 200:
            import json
            data = res.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        else:
            print("Gemini API error:", res.status_code, res.text)
    except Exception as e:
        print("Gemini enrichment failed, falling back to raw feed parsing:", e)
    return None

def build_fallback_current_affairs(today_str):
    """
    Fallback method that works directly with RSS feeds without requiring any API keys.
    """
    data = {}
    for cat, feed_url in RSS_FEEDS.items():
        feed_items = fetch_feed_items(feed_url, limit=3)
        formatted = []
        for it in feed_items:
            title = it["title"]
            summary = it["summary"]
            # Derive reasonable exam pointer
            exam_pointer = "Crucial for General Awareness (GA/GK) tier-1 & tier-2 objective questions."
            if "RBI" in title or "Bank" in title:
                exam_pointer = "Static GK: RBI HQ: Mumbai | Established: 1 April 1935 (RBI Act 1934)"
            elif "ISRO" in title:
                exam_pointer = "Static GK: ISRO HQ: Bengaluru | Founded: 15 Aug 1969 | Space Commission: 1972"
            elif "DRDO" in title:
                exam_pointer = "Static GK: DRDO HQ: New Delhi | Formed: 1958 | Ministry of Defence"
            
            formatted.append({
                "title": title,
                "points": [
                    summary if len(summary) > 20 else title,
                    "Regularly asked in SSC CGL, CHSL, Railway RRB & State PSC exams."
                ],
                "exam_pointer": exam_pointer
            })
        data[cat] = formatted

    # Add default daily booster quiz
    data["daily_quiz"] = [
        {
            "question": f"Which organization released today's major economic/governance bulletin for {today_str}?",
            "options": ["A) Reserve Bank of India", "B) NITI Aayog", "C) Ministry of Finance", "D) State Bank of India"],
            "answer": "A) Reserve Bank of India - Key regulatory updates released periodically."
        },
        {
            "question": "What is the headquarters location of ISRO?",
            "options": ["A) New Delhi", "B) Bengaluru", "C) Hyderabad", "D) Chennai"],
            "answer": "B) Bengaluru, Karnataka (Founded: 1969)."
        },
        {
            "question": "Who acts as the ex-officio Chairman of NITI Aayog?",
            "options": ["A) President of India", "B) Prime Minister of India", "C) Finance Minister", "D) RBI Governor"],
            "answer": "B) Prime Minister of India."
        }
    ]
    return data

def fetch_all_current_affairs():
    today = datetime.datetime.now()
    today_str = today.strftime("%A, %d %B %Y")
    
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    
    # If API key is available, we can gather raw headlines and pass to Gemini
    if gemini_api_key:
        print("Using Gemini API for high-yield SSC formatting...")
        raw_summary = {}
        for cat, feed_url in RSS_FEEDS.items():
            raw_summary[cat] = [item["title"] for item in fetch_feed_items(feed_url, limit=4)]
        
        enhanced = get_gemini_enhanced_content(raw_summary, today_str, gemini_api_key)
        if enhanced:
            enhanced["date_str"] = today_str
            return enhanced

    print("Fetching direct RSS feeds (Zero API key mode)...")
    fallback = build_fallback_current_affairs(today_str)
    fallback["date_str"] = today_str
    return fallback

if __name__ == "__main__":
    affairs = fetch_all_current_affairs()
    print("Fetched successfully. Date:", affairs.get("date_str"))
    print("Categories:", list(affairs.keys()))
