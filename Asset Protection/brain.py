from flask import Flask, request, jsonify
from database import db
import cv2
import imagehash
import yt_dlp
from PIL import Image
from firebase_admin import firestore
import requests

app = Flask(__name__)

def get_stream_url(url):
    """Extracts a low-res stream URL to save bandwidth during processing."""
    ydl_opts = {
        "format": "best[height<=360]", 
        "quiet": True, 
        "no_warnings": True,
        "skip_download": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['url']

def extract_fingerprints(video_url):
    """Captures perceptual hashes every 1 second of video."""
    try:
        stream_url = get_stream_url(video_url)
        cap = cv2.VideoCapture(stream_url)
        hashes = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            # Sample 1 frame per second (assuming ~30fps)
            if frame_count % 30 == 0:
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img_rgb)
                phash = str(imagehash.phash(pil_img))
                hashes.append(phash)
            frame_count += 1
            
        cap.release()
        return hashes
    except Exception as e:
        print(f"Hashing Error: {e}")
        return []

@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    video_url = data.get("url")
    is_scan_only = data.get("scan_only", False) # If true, we don't save, we just compare

    print(f"🧠 Processing: {video_url} (Scan Only: {is_scan_only})")
    current_hashes = extract_fingerprints(video_url)
    
    if not current_hashes:
        return jsonify({"error": "Failed to process video"}), 500

    if not is_scan_only:
        # MASTER MODE: Save this as the original content to protect
        asset_ref = db.collection("protected_assets").document()
        asset_ref.set({
            "url": video_url,
            "hashes": current_hashes,
            "created_at": firestore.SERVER_TIMESTAMP
        })
        return jsonify({"status": "protected", "asset_id": asset_ref.id})
    
    else:
        # SCAN MODE: Compare against all originals in the DB
        verdict = {"status": "safe", "match_score": 0, "matched_with": None}
        all_originals = db.collection("protected_assets").stream()
        
        for original in all_originals:
            orig_data = original.to_dict()
            orig_hashes = orig_data.get("hashes", [])
            
            # Check how many frames overlap (Hamming distance threshold of 8)
            matches = 0
            for h in current_hashes:
                h_obj = imagehash.hex_to_hash(h)
                for oh in orig_hashes:
                    if h_obj - imagehash.hex_to_hash(oh) < 8:
                        matches += 1
                        break
            
            score = (matches / len(current_hashes)) * 100 if current_hashes else 0
            
            if score > 25: # Threshold for 'suspicious'
                verdict = {
                    "status": "🚨 PIRATED" if score > 70 else "⚠️ SUSPICIOUS",
                    "match_score": round(score, 2),
                    "matched_with": orig_data['url']
                }
                break

        return jsonify(verdict)

if __name__ == "__main__":
    # Run the brain on port 5000
    app.run(port=5000)