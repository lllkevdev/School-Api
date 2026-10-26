from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session

from core import config
from models.usuario import Usuario


def _resolver_ruta(clave: str) -> Path:
    media_root = config.MEDIA_ROOT.resolve()
    ruta = (media_root / clave).resolve()

    if not ruta.is_relative_to(media_root):
        raise ValueError("Ruta de foto inválida")

    return ruta


def _borrar_archivo(clave: str | None) -> None:
    if not clave:
        return

    try:
        ruta = _resolver_ruta(clave)
        ruta.unlink(missing_ok=True)
    except (OSError, ValueError):
        pass


def _convertir_a_webp(
    contenido: bytes,
) -> tuple[bytes | None, str | None]:
    try:
        with Image.open(BytesIO(contenido)) as original:
            formato = (original.format or "").upper()

            if formato not in config.FOTO_FORMATOS_PERMITIDOS:
                return None, "foto_formato_invalido"

            if original.width * original.height > config.FOTO_MAX_PIXELES:
                return None, "foto_invalida"

            imagen = ImageOps.exif_transpose(original)
            imagen.thumbnail(
                (
                    config.FOTO_MAX_DIMENSION,
                    config.FOTO_MAX_DIMENSION,
                ),
                Image.Resampling.LANCZOS,
            )

            tiene_alfa = imagen.mode in {"RGBA", "LA"} or (
                imagen.mode == "P"
                and "transparency" in imagen.info
            )
            imagen = imagen.convert("RGBA" if tiene_alfa else "RGB")

            salida = BytesIO()
            imagen.save(
                salida,
                format="WEBP",
                quality=85,
                method=6,
            )

            return salida.getvalue(), None

    except UnidentifiedImageError:
        return None, "foto_invalida"
    except Image.DecompressionBombError:
        return None, "foto_invalida"
    except (OSError, ValueError):
        return None, "foto_invalida"


def guardar_archivo_foto(
    contenido: bytes,
) -> tuple[str | None, str | None]:
    if not contenido:
        return None, "foto_invalida"

    if len(contenido) > config.MAX_FOTO_BYTES:
        return None, "foto_muy_grande"

    contenido_webp, error = _convertir_a_webp(contenido)

    if error is not None:
        return None, error

    if contenido_webp is None:
        return None, "foto_invalida"

    clave = f"fotos_perfil/{uuid4().hex}.webp"
    ruta = _resolver_ruta(clave)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta_temporal = ruta.with_suffix(".tmp")

    try:
        ruta_temporal.write_bytes(contenido_webp)
        ruta_temporal.replace(ruta)
    except OSError:
        ruta_temporal.unlink(missing_ok=True)
        raise

    return clave, None


def obtener_ruta_foto(
    usuario: Usuario,
) -> Path | None:
    if not usuario.foto_perfil:
        return None

    try:
        ruta = _resolver_ruta(usuario.foto_perfil)
    except ValueError:
        return None

    if not ruta.is_file():
        return None

    return ruta


def actualizar_foto(
    db: Session,
    usuario: Usuario,
    contenido: bytes,
) -> tuple[Usuario | None, str | None]:
    clave, error = guardar_archivo_foto(contenido)
    if error is not None:
        return None, error

    anterior = usuario.foto_perfil
    usuario.foto_perfil = clave

    try:
        db.commit()
        db.refresh(usuario)
    except Exception:
        db.rollback()
        _borrar_archivo(clave)
        raise

    _borrar_archivo(anterior)

    return usuario, None


def eliminar_foto(
    db: Session,
    usuario: Usuario,
) -> tuple[Usuario | None, str | None]:
    anterior = usuario.foto_perfil

    if anterior is None:
        return usuario, None

    usuario.foto_perfil = None

    try:
        db.commit()
        db.refresh(usuario)
    except Exception:
        db.rollback()
        raise

    _borrar_archivo(anterior)

    return usuario, None
