import firebase_admin
from firebase_admin import credentials, firestore
import os

def init_db():
    firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")
    firebase_private_key_id = os.getenv("FIREBASE_PRIVATE_KEY_ID")
    firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY")
    firebase_client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
    firebase_client_id = os.getenv("FIREBASE_CLIENT_ID")
    firebase_client_x509_cert_url = os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
    firebase_auth_uri = os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    firebase_token_uri = os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token")
    firebase_auth_provider_x509_cert_url = os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")
    firebase_universe_domain = os.getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")

    if not all([firebase_project_id, firebase_private_key_id, firebase_private_key, firebase_client_email, firebase_client_id]):
        raise ValueError(
            "Firebase environment variables are required. Set FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY_ID, "
            "FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL, and FIREBASE_CLIENT_ID."
        )

    firebase_private_key = firebase_private_key.replace("\\n", "\n")

    service_account_info = {
        "type": "service_account",
        "project_id": firebase_project_id,
        "private_key_id": firebase_private_key_id,
        "private_key": firebase_private_key,
        "client_email": firebase_client_email,
        "client_id": firebase_client_id,
        "auth_uri": firebase_auth_uri,
        "token_uri": firebase_token_uri,
        "auth_provider_x509_cert_url": firebase_auth_provider_x509_cert_url,
        "client_x509_cert_url": firebase_client_x509_cert_url or f"https://www.googleapis.com/robot/v1/metadata/x509/{firebase_client_email}",
        "universe_domain": firebase_universe_domain,
    }

    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
        print("✅ Connected to Google Firebase")

    return firestore.client()

# Global database instance
db = init_db()