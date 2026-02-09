import os
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app

load_dotenv()

private_key = os.getenv("FIREBASE_PRIVATE_KEY")

if not private_key:
    raise RuntimeError("FIREBASE_PRIVATE_KEY não foi carregada do .env")

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "private_key": private_key.replace("\\n", "\n"),
    "token_uri": "https://oauth2.googleapis.com/token",
})

initialize_app(cred)
