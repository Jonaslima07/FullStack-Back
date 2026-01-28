import firebase_admin
from firebase_admin import credentials

print("📦 Carregando Firebase Admin...")

if not firebase_admin._apps:
    cred = credentials.Certificate(
        "helpers/firebase/fullstock-d8094-firebase-adminsdk-fbsvc-a2b1c6d4b6.json"
    )
    firebase_admin.initialize_app(cred)
    print("🔥 Firebase Admin inicializado")
else:
    print("⚠️ Firebase Admin já estava inicializado")
