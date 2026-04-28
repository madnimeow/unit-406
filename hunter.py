import os
import google.generativeai as genai
from googleapiclient.discovery import build
from database import db
import requests

# 🔑 Load keys from environment variables
GEMINI_KEY = os.getenv("GEMINI_KEY")
YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")

if not GEMINI_KEY:
    raise ValueError("GEMINI_KEY not set in environment variables")
if not YOUTUBE_KEY:
    raise ValueError("YOUTUBE_KEY not set in environment variables")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)

def get_ai_search_queries(original_title):
    """Uses Gemini to generate search queries piraters would use."""
    prompt = f"Original Video: '{original_title}'. Give me 3 short search queries to find re-uploads or pirated highlights of this. Return only queries separated by commas."
    try:
        response = model.generate_content(prompt)
        return [q.strip() for q in response.text.split(",")]
    except:
        return [original_title] # Fallback

def hunt(master_url):
    """Finds suspects and sends them to the Brain for analysis."""
    # 1. Get original title from YouTube
    video_id = master_url.split("v=")[-1]
    request = youtube.videos().list(part="snippet", id=video_id)
    response = request.execute()
    
    if not response['items']: return "Master video not found."
    title = response['items'][0]['snippet']['title']
    
    # 2. Get AI-powered search terms
    queries = get_ai_search_queries(title)
    print(f"🔎 AI Hunting Queries: {queries}")
    
    for q in queries:
        search_req = youtube.search().list(q=q, part="snippet", type="video", maxResults=5)
        search_res = search_req.execute()
        
        for item in search_res.get('items', []):
            suspect_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            if suspect_url == master_url: continue # Skip the original
            
            # 3. Send to Brain for Comparison
            print(f"🧐 Analyzing Suspect: {item['snippet']['title']}")
            report = requests.post("http://127.0.0.1:5000/process", json={
                "url": suspect_url,
                "scan_only": True
            }).json()

            if "status" in report and report["status"] != "safe":
                db.collection("alerts").add({
                    "suspect_url": suspect_url,
                    "title": item['snippet']['title'],
                    "status": report.get('status', 'Unknown'), # Use .get() to avoid crashes
                    "score": report.get('match_score', 0),
                    "original": master_url
                })
            else:
                print(f"Skipping {suspect_url}: Brain returned {report}")
            
            # 4. Save Verdict if pirated
            if report.get("status") != "safe":
                db.collection("alerts").add({
                    "suspect_url": suspect_url,
                    "title": item['snippet']['title'],
                    "status": report['status'],
                    "score": report['match_score'],
                    "original": master_url
                })