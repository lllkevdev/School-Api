import os 

from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY") or ""

ACCES_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCES_TOKEN_EXPIRES_MINUTES", "30")
)

if SECRET_KEY is None:
    raise ValueError("SECRET_KEY no está configurada")