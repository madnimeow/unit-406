import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env explicitly
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

print("📂 ENV FILE LOADED FROM:", env_path)

# 🔑 Test basic API keys
print("\n--- API KEYS ---")
print("GEMINI_KEY:", os.getenv("GEMINI_KEY"))
print("YOUTUBE_KEY:", os.getenv("YOUTUBE_KEY"))

# 🔥 Test Firebase fields
print("\n--- FIREBASE ---")
print("PROJECT_ID:", os.getenv("FIREBASE_PROJECT_ID"))
print("CLIENT_EMAIL:", os.getenv("FIREBASE_CLIENT_EMAIL"))

# 🔐 Test private key formatting
private_key = os.getenv("FIREBASE_PRIVATE_KEY")

if private_key:
    print("\n--- PRIVATE KEY CHECK ---")
    
    # Check raw
    print("Length:", len(private_key))
    
    # Convert \n → actual newline
    fixed_key = private_key.replace("\\n", "\n")
    
    print("Has BEGIN:", "BEGIN PRIVATE KEY" in fixed_key)
    print("Has END:", "END PRIVATE KEY" in fixed_key)
    print("Newlines present:", "\n" in fixed_key)
else:
    print("❌ FIREBASE_PRIVATE_KEY not found")

print("\n✅ TEST COMPLETE")