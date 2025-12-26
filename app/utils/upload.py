import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

# =========================================================
# CONFIGURAÇÕES
# =========================================================

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

UPLOAD_SUBDIR = "uploads/logos"


# =========================================================
# HELPERS
# =========================================================

def allowed_file(filename: str) -> bool:
    """
    Verifica se a extensão do arquivo é permitida
    """
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def save_logo(file_storage) -> str:
    """
    Salva a logo da barbearia e retorna o nome do arquivo salvo.

    Retorno:
        str -> nome do arquivo (para salvar no banco)
    """

    if not file_storage or file_storage.filename == "":
        raise ValueError("Arquivo inválido")

    if not allowed_file(file_storage.filename):
        raise ValueError("Formato de imagem não permitido")

    # Nome seguro + UUID
    original_name = secure_filename(file_storage.filename)
    ext = original_name.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    # Caminho absoluto
    upload_root = os.path.join(
        current_app.root_path,
        "static",
        UPLOAD_SUBDIR
    )

    # Garante que a pasta existe
    os.makedirs(upload_root, exist_ok=True)

    file_path = os.path.join(upload_root, filename)

    # Salva o arquivo
    file_storage.save(file_path)

    return filename


def delete_logo(filename: str):
    """
    Remove uma logo existente do disco (se existir)
    """
    if not filename:
        return

    file_path = os.path.join(
        current_app.root_path,
        "static",
        UPLOAD_SUBDIR,
        filename
    )

    if os.path.exists(file_path):
        os.remove(file_path)
