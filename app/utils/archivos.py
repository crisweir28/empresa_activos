# app/utils/archivos.py
"""
Helper reutilizable para subida de archivos (imágenes y documentos).
Usado por Almacén y TI.
"""
import os
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

# ── Extensiones permitidas ────────────────────────────────────
EXTENSIONES_IMAGEN     = {"png", "jpg", "jpeg", "gif", "webp"}
EXTENSIONES_DOCUMENTO  = {"pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv"}
EXTENSIONES_PERMITIDAS = EXTENSIONES_IMAGEN | EXTENSIONES_DOCUMENTO

# ── MIME types de documentos ──────────────────────────────────
MIME_ICONOS = {
    "application/pdf":                                                   "📄",
    "application/msword":                                                "📝",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "📝",
    "application/vnd.ms-excel":                                          "📊",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "📊",
    "application/vnd.ms-powerpoint":                                     "📑",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "📑",
    "text/plain":                                                        "📃",
    "text/csv":                                                          "📊",
}


def extension_permitida(filename: str) -> bool:
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


def es_imagen(filename: str) -> bool:
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in EXTENSIONES_IMAGEN


def tipo_archivo(filename: str) -> str:
    """Devuelve 'imagen' o 'documento'."""
    return "imagen" if es_imagen(filename) else "documento"


def guardar_archivo(archivo, prefijo: str, carpeta: str = "documents") -> dict:
    """
    Guarda un archivo en la carpeta indicada y devuelve un dict con:
    - filename: nombre seguro del archivo
    - url: ruta relativa para guardar en BD
    - tipo_archivo: 'imagen' o 'documento'
    - mime_type: tipo MIME detectado
    - ruta_absoluta: path completo en disco

    Parámetros:
    - archivo: FileStorage de Flask
    - prefijo: ej. 'herr_5' o 'equipo_3'
    - carpeta: 'documents' o 'static/evidencias'
    """
    if not archivo or archivo.filename == "":
        raise ValueError("No se seleccionó ningún archivo.")

    if not extension_permitida(archivo.filename):
        raise ValueError(
            f"Tipo de archivo no permitido. "
            f"Extensiones válidas: {', '.join(sorted(EXTENSIONES_PERMITIDAS))}"
        )

    # Nombre seguro con timestamp para evitar colisiones
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext      = archivo.filename.rsplit(".", 1)[1].lower()
    filename = secure_filename(f"{prefijo}_{ts}.{ext}")

    # Ruta de destino
    if carpeta == "documents":
        dest_dir = os.path.join(current_app.root_path, "documents")
        url_rel  = f"/administrativo/documents/{filename}"
    else:
        dest_dir = os.path.join(current_app.root_path, "static", "evidencias")
        url_rel  = f"/static/evidencias/{filename}"

    os.makedirs(dest_dir, exist_ok=True)
    ruta_abs = os.path.join(dest_dir, filename)
    archivo.save(ruta_abs)

    # MIME type
    mime, _ = mimetypes.guess_type(filename)
    mime     = mime or "application/octet-stream"

    return {
        "filename":      filename,
        "url":           url_rel,
        "tipo_archivo":  tipo_archivo(filename),
        "mime_type":     mime,
        "ruta_absoluta": ruta_abs,
    }


def icono_mime(mime_type: str) -> str:
    return MIME_ICONOS.get(mime_type, "📎")