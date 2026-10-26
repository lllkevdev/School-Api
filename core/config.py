import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = Path(
    os.getenv("MEDIA_ROOT", BASE_DIR / "media")
).expanduser().resolve()

MAX_FOTO_BYTES = int(
    os.getenv("MAX_FOTO_BYTES", str(2 * 1024 * 1024))
)

FOTO_MAX_DIMENSION = int(
    os.getenv("FOTO_MAX_DIMENSION", "1024")
)

FOTO_MAX_PIXELES = int(
    os.getenv("FOTO_MAX_PIXELES", "25000000")
)

FOTO_FORMATOS_PERMITIDOS = frozenset({"JPEG", "PNG", "WEBP"})


SECRET_KEY = os.getenv("SECRET_KEY")


ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCES_TOKEN_EXPIRES_MINUTES", "30")
)

if SECRET_KEY is None:
    raise ValueError("SECRET_KEY no está configurada")