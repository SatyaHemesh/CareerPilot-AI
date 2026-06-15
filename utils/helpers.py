import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
REPORT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    """Save an uploaded file with a unique name. Returns (filename, filepath)."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'pdf'
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(filepath)
    return unique_filename, filepath


def get_report_path(user_id, report_id):
    os.makedirs(REPORT_FOLDER, exist_ok=True)
    return os.path.join(REPORT_FOLDER, f"report_{user_id}_{report_id}.pdf")


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def truncate_text(text, max_length=200):
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def safe_json_loads(text, default=None):
    import json
    try:
        return json.loads(text)
    except Exception:
        return default if default is not None else {}
