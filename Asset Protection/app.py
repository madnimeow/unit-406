import streamlit as st
import requests
from database import db
from hunter import hunt

st.set_page_config(page_title="Asset Guard", page_icon="🛡️")

st.title("🛡️ Asset Guard")
st.subheader("AI-Powered Video Piracy Detection")

tab1, tab2 = st.tabs(["Protect Content", "Active Alerts"])

with tab1:
    master_url = st.text_input("Enter Original Video URL to Protect")
    if st.button("Start Protection & AI Hunt"):
        with st.spinner("Fingerprinting and Hunting..."):
            # Step 1: Register as Master in the Brain
            resp = requests.post("http://127.0.0.1:5000/process", json={"url": master_url, "scan_only": False})
            if resp.status_code == 200:
                st.success("✅ Content Protected! AI Hunter is now searching YouTube...")
                # Step 2: Trigger the Hunter
                hunt(master_url)
                st.info("Hunt Complete. Check Alerts tab.")
            else:
                st.error("Failed to process master video.")

with tab2:
    st.header("🏴‍☠️ Piracy Detections")
    alerts = db.collection("alerts").order_by("score", direction="DESCENDING").stream()
    
    found = False
    for alert in alerts:
        found = True
        data = alert.to_dict()
        with st.expander(f"{data['status']} - {data['score']}% Match"):
            st.write(f"**Suspect Title:** {data['title']}")
            st.write(f"**Link:** {data['suspect_url']}")
            st.write(f"**Matched With:** {data['original']}")
            st.video(data['suspect_url'])
            
    if not found:
        st.write("No piracy detected yet.")