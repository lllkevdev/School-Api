from io import BytesIO

import pytest
from PIL import Image

from core import config


@pytest.fixture
def media_root(tmp_path, monkeypatch):
    root = tmp_path / "media"
    monkeypatch.setattr(config, "MEDIA_ROOT", root)
    return root


def crear_imagen(
    formato: str = "PNG",
    tamano: tuple[int, int] = (1600, 900),
    modo: str = "RGB",
) -> bytes:
    salida = BytesIO()
    color = (126, 34, 206, 255) if modo == "RGBA" else (126, 34, 206)
    imagen = Image.new(modo, tamano, color)

    try:
        imagen.save(salida, format=formato)
    finally:
        imagen.close()

    return salida.getvalue()


def subir_foto(client, headers, contenido, nombre="avatar.png", tipo="image/png"):
    return client.post(
        "/perfil/me/foto",
        headers=headers,
        files={"foto": (nombre, contenido, tipo)},
    )


def test_subir_foto_admin(client, auth_headers_admin, media_root):
    contenido = crear_imagen(modo="RGBA")

    respuesta = subir_foto(client, auth_headers_admin, contenido)

    assert respuesta.status_code == 200

    datos = respuesta.json()
    clave = datos["usuario"]["foto_perfil"]

    assert clave is not None
    assert clave.startswith("fotos_perfil/")
    assert clave.endswith(".webp")
    assert "avatar.png" not in clave

    ruta = media_root / clave

    assert ruta.is_file()

    with Image.open(ruta) as imagen:
        assert imagen.format == "WEBP"
        assert max(imagen.size) <= config.FOTO_MAX_DIMENSION

    perfil = client.get("/perfil/me", headers=auth_headers_admin)

    assert perfil.status_code == 200
    assert perfil.json()["usuario"]["foto_perfil"] == clave


def test_obtener_foto_autenticada(client, auth_headers_admin, media_root):
    subida = subir_foto(
        client,
        auth_headers_admin,
        crear_imagen(),
    )

    assert subida.status_code == 200

    respuesta = client.get(
        "/perfil/me/foto",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == "image/webp"
    assert respuesta.headers["cache-control"] == "private, no-store"
    assert respuesta.headers["x-content-type-options"] == "nosniff"
    assert respuesta.content.startswith(b"RIFF")
    assert respuesta.content[8:12] == b"WEBP"


def test_reemplazar_foto_elimina_archivo_anterior(
    client,
    auth_headers_admin,
    media_root,
):
    primera = subir_foto(
        client,
        auth_headers_admin,
        crear_imagen(),
    )
    clave_anterior = primera.json()["usuario"]["foto_perfil"]
    ruta_anterior = media_root / clave_anterior

    assert ruta_anterior.is_file()

    segunda = subir_foto(
        client,
        auth_headers_admin,
        crear_imagen(tamano=(800, 600)),
    )
    clave_nueva = segunda.json()["usuario"]["foto_perfil"]
    ruta_nueva = media_root / clave_nueva

    assert segunda.status_code == 200
    assert clave_nueva != clave_anterior
    assert not ruta_anterior.exists()
    assert ruta_nueva.is_file()


def test_eliminar_foto(client, auth_headers_admin, media_root):
    subida = subir_foto(
        client,
        auth_headers_admin,
        crear_imagen(),
    )
    clave = subida.json()["usuario"]["foto_perfil"]
    ruta = media_root / clave

    assert ruta.is_file()

    respuesta = client.delete(
        "/perfil/me/foto",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["usuario"]["foto_perfil"] is None
    assert not ruta.exists()

    foto = client.get(
        "/perfil/me/foto",
        headers=auth_headers_admin,
    )

    assert foto.status_code == 404


def test_eliminar_foto_sin_foto_es_idempotente(
    client,
    auth_headers_admin,
    media_root,
):
    respuesta = client.delete(
        "/perfil/me/foto",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["usuario"]["foto_perfil"] is None


def test_obtener_foto_sin_foto(client, auth_headers_admin, media_root):
    respuesta = client.get(
        "/perfil/me/foto",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Foto de perfil no encontrada"


def test_subir_foto_alumno(client, auth_headers_alumno, media_root):
    respuesta = subir_foto(
        client,
        auth_headers_alumno,
        crear_imagen(),
    )

    assert respuesta.status_code == 200

    datos = respuesta.json()

    assert datos["usuario"]["foto_perfil"] is not None
    assert datos["alumno"]["documento_identidad"] == "12345678"


def test_subir_foto_formato_no_permitido(
    client,
    auth_headers_admin,
    media_root,
):
    respuesta = subir_foto(
        client,
        auth_headers_admin,
        crear_imagen(formato="GIF", tamano=(10, 10)),
        tipo="image/gif",
    )

    assert respuesta.status_code == 415


def test_subir_archivo_que_no_es_imagen(
    client,
    auth_headers_admin,
    media_root,
):
    respuesta = subir_foto(
        client,
        auth_headers_admin,
        b"esto no es una imagen",
    )

    assert respuesta.status_code == 400


def test_subir_foto_demasiado_grande(
    client,
    auth_headers_admin,
    media_root,
    monkeypatch,
):
    monkeypatch.setattr(config, "MAX_FOTO_BYTES", 10)

    respuesta = subir_foto(
        client,
        auth_headers_admin,
        b"12345678901",
    )

    assert respuesta.status_code == 413


def test_subir_foto_con_demasiados_pixeles(
    client,
    auth_headers_admin,
    media_root,
    monkeypatch,
):
    monkeypatch.setattr(config, "FOTO_MAX_PIXELES", 100)

    respuesta = subir_foto(
        client,
        auth_headers_admin,
        crear_imagen(tamano=(20, 20)),
    )

    assert respuesta.status_code == 400


def test_no_sirve_ruta_fuera_de_media_root(
    client,
    db,
    usuario_admin,
    auth_headers_admin,
    media_root,
):
    usuario_admin.foto_perfil = "../../fuera.webp"
    db.commit()

    respuesta = client.get(
        "/perfil/me/foto",
        headers=auth_headers_admin,
    )

    assert respuesta.status_code == 404


@pytest.mark.parametrize("metodo", ["get", "delete"])
def test_foto_requiere_autenticacion(client, media_root, metodo):
    respuesta = getattr(client, metodo)("/perfil/me/foto")

    assert respuesta.status_code == 401


def test_subir_foto_requiere_autenticacion(client, media_root):
    respuesta = subir_foto(
        client,
        {},
        crear_imagen(),
    )

    assert respuesta.status_code == 401
