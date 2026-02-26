import json
import os
from pathlib import Path
from time import time


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = PROJECT_ROOT / "Data" / "FolderContext.json"

ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".rst", ".log", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env",
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs", ".cpp", ".c", ".h", ".hpp", ".go", ".rs",
    ".php", ".rb", ".swift", ".kt", ".kts", ".scala", ".sh", ".ps1", ".bat", ".cmd",
    ".html", ".css", ".scss", ".sql", ".xml", ".csv",
}

SKIP_DIR_NAMES = {
    ".git", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache",
    "node_modules", "dist", "build", ".next", ".idea", ".vscode",
}

MAX_FILES = 120
MAX_FILE_CHARS = 1800
MAX_TOTAL_CHARS = 36000
MAX_FILE_SIZE_BYTES = 512 * 1024

_context_cache = {"folder": None, "text": "", "built_at": 0.0}


def _default_state():
    return {"active_folder": None}


def _load_state():
    try:
        if not STATE_PATH.exists():
            return _default_state()
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return _default_state()
        return {"active_folder": data.get("active_folder")}
    except Exception:
        return _default_state()


def _save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _normalize_path(path_text: str) -> str:
    path = (path_text or "").strip().strip('"').strip("'")
    while path and path[-1] in ".!?,":
        path = path[:-1].strip()
    return os.path.expandvars(os.path.expanduser(path))


def set_active_folder(path_text: str) -> str:
    path = _normalize_path(path_text)
    if not path:
        return "Please provide a folder path."

    resolved = Path(path).resolve()
    if not resolved.exists():
        return f"Folder not found: {resolved}"
    if not resolved.is_dir():
        return f"That path is not a folder: {resolved}"

    state = _load_state()
    state["active_folder"] = str(resolved)
    _save_state(state)
    _context_cache["folder"] = None
    _context_cache["text"] = ""
    return f"Folder context enabled: {resolved}"


def clear_active_folder() -> str:
    state = _load_state()
    state["active_folder"] = None
    _save_state(state)
    _context_cache["folder"] = None
    _context_cache["text"] = ""
    return "Folder context cleared."


def get_active_folder() -> str:
    state = _load_state()
    return state.get("active_folder") or ""


def _looks_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            sample = f.read(2048)
        return b"\x00" in sample
    except Exception:
        return True


def _iter_candidate_files(folder: Path):
    count = 0
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d not in SKIP_DIR_NAMES]
        for filename in files:
            if count >= MAX_FILES:
                return
            path = Path(root) / filename
            if path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            try:
                if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    continue
            except OSError:
                continue
            if _looks_binary(path):
                continue
            count += 1
            yield path


def _build_context_text(folder: Path) -> str:
    chunks = []
    total_chars = 0
    file_count = 0

    for path in _iter_candidate_files(folder):
        if total_chars >= MAX_TOTAL_CHARS:
            break
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        snippet = raw.strip()
        if not snippet:
            continue
        snippet = snippet[:MAX_FILE_CHARS]
        relative = str(path.relative_to(folder))
        block = f"\n[FILE] {relative}\n{snippet}\n"
        if total_chars + len(block) > MAX_TOTAL_CHARS:
            break
        chunks.append(block)
        total_chars += len(block)
        file_count += 1

    if file_count == 0:
        return (
            f"Local folder context is enabled for: {folder}\n"
            "No readable text/code files were found in this folder."
        )

    return (
        f"Local folder context is enabled for: {folder}\n"
        f"Loaded {file_count} text/code files (truncated snippets).\n"
        "Use this context when relevant. If missing details, say what file/content is needed."
        + "".join(chunks)
    )


def get_folder_context_message() -> str:
    folder_text = get_active_folder()
    if not folder_text:
        return ""

    folder = Path(folder_text)
    if not folder.exists() or not folder.is_dir():
        return ""

    # Cache briefly to avoid rescanning each user message.
    now = time()
    if _context_cache["folder"] == str(folder) and (now - _context_cache["built_at"]) < 20:
        return _context_cache["text"]

    text = _build_context_text(folder)
    _context_cache["folder"] = str(folder)
    _context_cache["text"] = text
    _context_cache["built_at"] = now
    return text


def handle_folder_command(query: str) -> str:
    q = (query or "").strip()
    lower = q.lower()

    if not q:
        return ""

    if lower in {"clear folder context", "disable folder context", "stop folder context"}:
        return clear_active_folder()

    if lower in {"which folder", "active folder", "current folder context"}:
        active = get_active_folder()
        return f"Active folder context: {active}" if active else "No folder context is active."

    prefixes = [
        "use folder ",
        "set folder ",
        "work with folder ",
        "use this folder ",
        "set folder path ",
        "work on folder ",
        "focus on folder ",
    ]
    for prefix in prefixes:
        if lower.startswith(prefix):
            return set_active_folder(q[len(prefix):].strip())

    return ""
