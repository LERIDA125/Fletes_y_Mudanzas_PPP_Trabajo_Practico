"""Adaptador intercambiable para guardar fotos de remitos firmados (H10).

- Si `BLOB_READ_WRITE_TOKEN` está definido en el entorno, sube el archivo a Vercel Blob y devuelve
  su URL pública (`https://...`).
- Por defecto (MVP local / Docker / Vercel sin Blob Store), codifica la imagen como Data URL Base64
  (`data:<mime>;base64,...`) para persistirla directamente en `servicios.foto_remito_url`.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import urllib.request
import uuid

logger = logging.getLogger(__name__)


class AlmacenamientoRemitosHibrido:
    def __init__(self, blob_token: str | None = None) -> None:
        self._blob_token = (
            blob_token if blob_token is not None else os.environ.get("BLOB_READ_WRITE_TOKEN", "")
        ).strip()

    def guardar(
        self,
        *,
        id_servicio: int,
        contenido: bytes,
        content_type: str,
        nombre_archivo: str | None = None,
    ) -> str:
        mime = (content_type or "image/jpeg").strip().lower()
        if self._blob_token:
            try:
                return self._subir_vercel_blob(
                    id_servicio=id_servicio,
                    contenido=contenido,
                    content_type=mime,
                    nombre_archivo=nombre_archivo,
                )
            except Exception as exc:
                logger.warning(
                    "Fallo subida a Vercel Blob (%s); usando respaldo Base64 en BD.", exc
                )

        codificado = base64.b64encode(contenido).decode("ascii")
        return f"data:{mime};base64,{codificado}"

    def _subir_vercel_blob(
        self,
        *,
        id_servicio: int,
        contenido: bytes,
        content_type: str,
        nombre_archivo: str | None = None,
    ) -> str:
        ext = "jpg"
        if "png" in content_type:
            ext = "png"
        elif "webp" in content_type:
            ext = "webp"
        elif nombre_archivo and "." in nombre_archivo:
            ext = nombre_archivo.rsplit(".", 1)[-1].lower()[:5]

        pathname = f"remitos/servicio-{id_servicio}-{uuid.uuid4().hex[:8]}.{ext}"
        url = f"https://blob.vercel-storage.com/{pathname}"
        req = urllib.request.Request(
            url,
            data=contenido,
            method="PUT",
            headers={
                "Authorization": f"Bearer {self._blob_token}",
                "x-api-version": "7",
                "x-content-type": content_type,
                "Content-Type": content_type,
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            cuerpo = json.loads(resp.read().decode("utf-8"))
            url_publica = cuerpo.get("url")
            if isinstance(url_publica, str) and url_publica.startswith("http"):
                return url_publica
        raise RuntimeError("Vercel Blob no devolvió una URL pública válida")
