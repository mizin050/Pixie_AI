import asyncio
import json
import mimetypes
import os
import re
import tempfile
import threading
import time
import zipfile
from pathlib import Path

import requests
from PIL import ImageGrab
from dotenv import dotenv_values
import edge_tts


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
STATE_PATH = PROJECT_ROOT / "Data" / "TelegramState.json"
TMP_DIR = PROJECT_ROOT / "Data" / "temp"
MAX_TELEGRAM_UPLOAD_BYTES = 50 * 1024 * 1024
MAX_ZIP_SOURCE_BYTES = 350 * 1024 * 1024
env_vars = dotenv_values(ENV_PATH)

TELEGRAM_TOKEN = (
    env_vars.get("TelegramBotToken")
    or env_vars.get("TELEGRAM_BOT_TOKEN")
    or os.getenv("TelegramBotToken")
    or os.getenv("TELEGRAM_BOT_TOKEN")
    or ""
).strip()

DEFAULT_CHAT_ID = (
    env_vars.get("TelegramChatID")
    or env_vars.get("TELEGRAM_CHAT_ID")
    or os.getenv("TelegramChatID")
    or os.getenv("TELEGRAM_CHAT_ID")
    or ""
).strip()

ALLOWED_CHAT_ID = (
    env_vars.get("TelegramAllowedChatID")
    or env_vars.get("TELEGRAM_ALLOWED_CHAT_ID")
    or os.getenv("TelegramAllowedChatID")
    or os.getenv("TELEGRAM_ALLOWED_CHAT_ID")
    or ""
).strip()

ASSISTANT_VOICE = env_vars.get("AssistantVoice") or env_vars.get("ASSISTANT_VOICE") or "en-US-AriaNeural"
GROQ_API_KEY = (
    env_vars.get("GroqAPIKey")
    or env_vars.get("GROQ_API_KEY")
    or os.getenv("GroqAPIKey")
    or os.getenv("GROQ_API_KEY")
)

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else ""
FILE_URL = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else ""

_service_started = False
_service_lock = threading.Lock()
_browse_sessions = {}
_browse_lock = threading.Lock()


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"last_update_id": 0, "primary_chat_id": DEFAULT_CHAT_ID}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"last_update_id": 0, "primary_chat_id": DEFAULT_CHAT_ID}
        return {
            "last_update_id": int(data.get("last_update_id", 0)),
            "primary_chat_id": str(data.get("primary_chat_id", DEFAULT_CHAT_ID or "")).strip(),
        }
    except Exception:
        return {"last_update_id": 0, "primary_chat_id": DEFAULT_CHAT_ID}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _api(method: str, data=None, files=None, timeout=40):
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Missing Telegram bot token. Set TELEGRAM_BOT_TOKEN in .env.")
    url = f"{BASE_URL}/{method}"
    response = requests.post(url, data=data, files=files, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(str(payload))
    return payload.get("result")


def _answer_callback(callback_query_id: str, text: str = "", show_alert: bool = False) -> None:
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    if show_alert:
        payload["show_alert"] = True
    try:
        _api("answerCallbackQuery", data=payload)
    except Exception:
        pass


def _resolve_chat_id(chat_id: str = "") -> str:
    state = _load_state()
    chosen = str(chat_id or "").strip() or state.get("primary_chat_id") or DEFAULT_CHAT_ID
    return str(chosen).strip()


def _set_primary_chat(chat_id: str) -> None:
    state = _load_state()
    state["primary_chat_id"] = str(chat_id).strip()
    _save_state(state)


def send_text(text: str, chat_id: str = "") -> str:
    target = _resolve_chat_id(chat_id)
    if not target:
        return "No Telegram chat is linked yet. Send /start to your bot first."
    _api("sendMessage", data={"chat_id": target, "text": text})
    return "Sent to Telegram."


def _send_path(path: Path, chat_id: str = "", caption: str = "") -> str:
    target = _resolve_chat_id(chat_id)
    if not target:
        return "No Telegram chat is linked yet. Send /start to your bot first."
    if not path.exists():
        return f"File not found: {path}"
    if not path.is_file():
        return f"Not a file: {path}"

    suffix = path.suffix.lower()
    mime = mimetypes.guess_type(str(path))[0] or ""

    method = "sendDocument"
    field = "document"
    if suffix in {".jpg", ".jpeg", ".png", ".webp"} or mime.startswith("image/"):
        method = "sendPhoto"
        field = "photo"
    elif suffix in {".mp4", ".mov", ".mkv", ".webm"} or mime.startswith("video/"):
        method = "sendVideo"
        field = "video"
    elif suffix in {".mp3", ".wav", ".m4a", ".aac", ".flac"}:
        method = "sendAudio"
        field = "audio"
    elif suffix in {".ogg", ".oga", ".opus"}:
        method = "sendVoice"
        field = "voice"

    with open(path, "rb") as f:
        _api(
            method,
            data={"chat_id": target, "caption": caption} if caption else {"chat_id": target},
            files={field: (path.name, f)},
            timeout=180,
        )
    return f"Sent file: {path.name}"


def send_file(file_path: str, chat_id: str = "", caption: str = "") -> str:
    clean = str(file_path or "").strip().strip('"').strip("'")
    if not clean:
        return "Missing file path."
    resolved = Path(clean).expanduser().resolve()
    if not resolved.exists() or not resolved.is_file():
        return f"File not found: {resolved}"
    size = resolved.stat().st_size
    if size > MAX_TELEGRAM_UPLOAD_BYTES:
        size_mb = size / (1024 * 1024)
        return f"File too large for Telegram upload: {size_mb:.1f} MB (max 50 MB)."
    return _send_path(resolved, chat_id=chat_id, caption=caption)


def _zip_folder(folder: Path) -> tuple[Path, int, int, int]:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time() * 1000)
    base_name = f"{folder.name}_{stamp}"
    zip_path = TMP_DIR / f"{base_name}.zip"
    file_count = 0
    skipped_count = 0
    source_bytes = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build"}]
            for filename in files:
                full_path = Path(root) / filename
                try:
                    size = full_path.stat().st_size
                    if source_bytes + size > MAX_ZIP_SOURCE_BYTES:
                        skipped_count += 1
                        continue
                    rel_path = full_path.relative_to(folder)
                    zf.write(full_path, arcname=str(rel_path))
                    source_bytes += size
                    file_count += 1
                except Exception:
                    skipped_count += 1
                    continue
    return zip_path, file_count, skipped_count, source_bytes


def send_folder(folder_path: str, chat_id: str = "") -> str:
    clean = str(folder_path or "").strip().strip('"').strip("'")
    if not clean:
        return "Missing folder path."
    folder = Path(clean).expanduser().resolve()
    if not folder.exists():
        return f"Folder not found: {folder}"
    if not folder.is_dir():
        return f"Not a folder: {folder}"
    try:
        started_at = time.time()
        zip_path, file_count, skipped_count, source_bytes = _zip_folder(folder)
        if file_count == 0:
            return "No files were added to zip (folder empty or everything skipped)."

        zip_size = zip_path.stat().st_size if zip_path.exists() else 0
        if zip_size > MAX_TELEGRAM_UPLOAD_BYTES:
            zip_mb = zip_size / (1024 * 1024)
            return (
                f"Zip created but too large to send via bot: {zip_mb:.1f} MB. "
                "Max is 50 MB. Try a smaller subfolder."
            )

        result = _send_path(zip_path, chat_id=chat_id, caption=f"Folder ZIP: {folder.name}")
        elapsed = time.time() - started_at
        source_mb = source_bytes / (1024 * 1024)
        return (
            f"{result} | {file_count} files, {source_mb:.1f} MB source, "
            f"{zip_size / (1024 * 1024):.1f} MB zip, {skipped_count} skipped, {elapsed:.1f}s"
        )
    except Exception as exc:
        return f"Unable to zip folder: {exc}"


def _send_folder_async(folder_path: str, chat_id: str, announce_prefix: str = "Preparing folder ZIP") -> None:
    send_text(f"{announce_prefix}... this can take a bit for large folders.", chat_id=chat_id)
    result = send_folder(folder_path, chat_id=chat_id)
    send_text(result, chat_id=chat_id)


def send_screenshot(chat_id: str = "") -> str:
    target = _resolve_chat_id(chat_id)
    if not target:
        return "No Telegram chat is linked yet. Send /start to your bot first."
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_path = TMP_DIR / "telegram_screenshot.png"
    image = ImageGrab.grab()
    image.save(screenshot_path, format="PNG")
    return _send_path(screenshot_path, chat_id=target, caption="Current screen")


async def _tts_to_temp_mp3(text: str, out_path: Path) -> None:
    comm = edge_tts.Communicate(text, ASSISTANT_VOICE, pitch="+5Hz", rate="+13%")
    await comm.save(str(out_path))


def send_voice_note(text: str, chat_id: str = "") -> str:
    target = _resolve_chat_id(chat_id)
    if not target:
        return "No Telegram chat is linked yet. Send /start to your bot first."
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    voice_path = TMP_DIR / "telegram_voice.mp3"
    asyncio.run(_tts_to_temp_mp3(text, voice_path))
    # sendVoice may reject non-OGG in some clients, so fallback to sendAudio.
    try:
        with open(voice_path, "rb") as f:
            _api("sendVoice", data={"chat_id": target}, files={"voice": ("reply.mp3", f)})
    except Exception:
        with open(voice_path, "rb") as f:
            _api("sendAudio", data={"chat_id": target, "title": "Pixie reply"}, files={"audio": ("reply.mp3", f)})
    return "Sent voice reply to Telegram."


def _send_location(lat: str, lon: str, chat_id: str = "") -> str:
    target = _resolve_chat_id(chat_id)
    if not target:
        return "No Telegram chat is linked yet. Send /start to your bot first."
    _api("sendLocation", data={"chat_id": target, "latitude": lat, "longitude": lon})
    return "Sent location."


def _send_contact(phone: str, first_name: str, last_name: str = "", chat_id: str = "") -> str:
    target = _resolve_chat_id(chat_id)
    if not target:
        return "No Telegram chat is linked yet. Send /start to your bot first."
    data = {"chat_id": target, "phone_number": phone, "first_name": first_name}
    if last_name:
        data["last_name"] = last_name
    _api("sendContact", data=data)
    return "Sent contact."


def _send_poll(question: str, options: list[str], chat_id: str = "") -> str:
    target = _resolve_chat_id(chat_id)
    if not target:
        return "No Telegram chat is linked yet. Send /start to your bot first."
    _api("sendPoll", data={"chat_id": target, "question": question, "options": json.dumps(options)})
    return "Sent poll."


def _send_album(paths: list[Path], chat_id: str = "", caption: str = "") -> str:
    target = _resolve_chat_id(chat_id)
    if not target:
        return "No Telegram chat is linked yet. Send /start to your bot first."
    files = {}
    media = []
    idx = 0
    for p in paths:
        if not p.exists() or not p.is_file():
            continue
        suffix = p.suffix.lower()
        is_image = suffix in {".jpg", ".jpeg", ".png", ".webp"}
        is_video = suffix in {".mp4", ".mov", ".mkv", ".webm"}
        if not (is_image or is_video):
            continue
        idx += 1
        attach_name = f"file{idx}"
        media_item = {"type": "photo" if is_image else "video", "media": f"attach://{attach_name}"}
        if idx == 1 and caption:
            media_item["caption"] = caption
        media.append(media_item)
        files[attach_name] = (p.name, open(p, "rb"))
    if not media:
        for _, f in files.items():
            f[1].close()
        return "Album supports only image/video files."
    try:
        _api("sendMediaGroup", data={"chat_id": target, "media": json.dumps(media)}, files=files)
    finally:
        for _, f in files.items():
            f[1].close()
    return f"Sent album with {len(media)} item(s)."


def _extract_telegram_command(query: str) -> str:
    q = (query or "").strip()
    if not q:
        return ""
    lower = q.lower()
    prefixes = [
        "telegram ",
        "send on telegram ",
        "send to telegram ",
    ]
    for p in prefixes:
        if lower.startswith(p):
            return q[len(p):].strip()
    return ""


def handle_local_telegram_command(query: str) -> str:
    command = _extract_telegram_command(query)
    if not command:
        return ""
    if not TELEGRAM_TOKEN:
        return "Telegram bot token is missing. Add TELEGRAM_BOT_TOKEN in .env."

    c = command.strip()
    lower = c.lower()

    if lower in {"status", "help"}:
        chat = _resolve_chat_id("")
        return (
            "Telegram bridge is ready.\n"
            f"Active chat: {chat or 'not linked'}\n"
            "Commands: telegram send <text>, telegram file <path>, telegram folder <path>, telegram screenshot, telegram voice <text>, "
            "telegram location <lat>,<lon>, telegram contact <phone>|<first>|<last>, telegram poll <q>|<a>|<b>, "
            "telegram album <path1>|<path2>"
        )
    if lower.startswith("set chat "):
        chat_id = c[9:].strip()
        if not chat_id:
            return "Usage: telegram set chat <chat_id>"
        _set_primary_chat(chat_id)
        return f"Telegram chat set to: {chat_id}"
    if lower.startswith("send "):
        return send_text(c[5:].strip())
    if lower.startswith("file "):
        return send_file(c[5:].strip())
    if lower.startswith("folder "):
        target_folder = c[7:].strip()
        thread = threading.Thread(
            target=_send_folder_async,
            args=(target_folder, _resolve_chat_id(""), "Preparing folder ZIP for Telegram"),
            daemon=True,
        )
        thread.start()
        return "Started folder zip/send job for Telegram."
    if lower.startswith("screenshot"):
        return send_screenshot()
    if lower.startswith("voice "):
        return send_voice_note(c[6:].strip())
    if lower.startswith("location "):
        payload = c[9:].strip()
        if "," not in payload:
            return "Usage: telegram location <latitude>,<longitude>"
        lat, lon = [x.strip() for x in payload.split(",", 1)]
        return _send_location(lat, lon)
    if lower.startswith("contact "):
        payload = c[8:].strip()
        parts = [x.strip() for x in payload.split("|")]
        if len(parts) < 2:
            return "Usage: telegram contact <phone>|<first_name>|<last_name_optional>"
        return _send_contact(parts[0], parts[1], parts[2] if len(parts) > 2 else "")
    if lower.startswith("poll "):
        payload = c[5:].strip()
        parts = [x.strip() for x in payload.split("|") if x.strip()]
        if len(parts) < 3:
            return "Usage: telegram poll <question>|<option1>|<option2>..."
        return _send_poll(parts[0], parts[1:])
    if lower.startswith("album "):
        payload = c[6:].strip()
        paths = [Path(x.strip().strip('"').strip("'")).expanduser().resolve() for x in payload.split("|") if x.strip()]
        return _send_album(paths)
    return "Unknown Telegram command. Use: telegram help"


def _transcribe_ogg(ogg_path: Path) -> str:
    if not GROQ_API_KEY:
        return ""
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        with open(ogg_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=(ogg_path.name, f.read()),
                model="whisper-large-v3-turbo",
                response_format="json",
                language="en",
                temperature=0.0,
            )
        text = getattr(transcription, "text", "") or ""
        return text.strip()
    except Exception:
        return ""


def _reply_with_pixie(prompt: str) -> str:
    from Backend.Model import FirstLayerDMM
    from Backend.SpeechToText import QueryModifier
    from Backend.RealtimeSearchEngine import RealtimeSearchEngine
    from Backend.Chatbot import chatBot

    cleaned = QueryModifier(prompt)
    decisions = FirstLayerDMM(cleaned)
    is_realtime = any(i.startswith("realtime") for i in decisions)
    merged = " and ".join(
        [" ".join(i.split()[1:]) for i in decisions if i.startswith("general") or i.startswith("realtime")]
    )
    if is_realtime:
        return RealtimeSearchEngine(QueryModifier(merged or cleaned))
    for decision in decisions:
        if decision.startswith("general"):
            return chatBot(QueryModifier(decision.replace("general ", "", 1)))
    return chatBot(cleaned)


def _download_telegram_file(file_id: str, suffix: str = ".bin") -> Path:
    result = _api("getFile", data={"file_id": file_id})
    file_path = result.get("file_path")
    if not file_path:
        raise RuntimeError("Unable to resolve Telegram file path.")
    url = f"{FILE_URL}/{file_path}"
    resp = requests.get(url, timeout=40)
    resp.raise_for_status()
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    local_path = TMP_DIR / f"tg_{int(time.time() * 1000)}{suffix}"
    with open(local_path, "wb") as f:
        f.write(resp.content)
    return local_path


def _allowed_chat(chat_id: str) -> bool:
    if not ALLOWED_CHAT_ID:
        return True
    return str(chat_id) == str(ALLOWED_CHAT_ID)


def _get_or_create_chat_session(chat_id: str) -> dict:
    with _browse_lock:
        session = _browse_sessions.get(chat_id)
        if session is None:
            session = {
                "id_to_path": {},
                "path_to_id": {},
                "next_id": 1,
                "file_filter": "all",
                "sort_mode": "recent",
                "current_sid": "",
            }
            _browse_sessions[chat_id] = session
        return session


def _register_path(chat_id: str, path: Path) -> str:
    session = _get_or_create_chat_session(chat_id)
    path_text = str(path.resolve())
    existing = session["path_to_id"].get(path_text)
    if existing:
        return existing
    sid = str(session["next_id"])
    session["next_id"] += 1
    session["id_to_path"][sid] = path_text
    session["path_to_id"][path_text] = sid
    return sid


def _resolve_sid_path(chat_id: str, sid: str) -> Path | None:
    session = _get_or_create_chat_session(chat_id)
    path_text = session["id_to_path"].get(sid)
    if not path_text:
        return None
    path = Path(path_text)
    if not path.exists():
        return None
    return path


def _set_browser_preferences(chat_id: str, file_filter: str | None = None, sort_mode: str | None = None) -> dict:
    session = _get_or_create_chat_session(chat_id)
    if file_filter is not None:
        session["file_filter"] = file_filter
    if sort_mode is not None:
        session["sort_mode"] = sort_mode
    return session


def _get_browser_preferences(chat_id: str) -> tuple[str, str]:
    session = _get_or_create_chat_session(chat_id)
    return session.get("file_filter", "all"), session.get("sort_mode", "recent")


def _quick_roots() -> list[tuple[str, Path]]:
    roots = []
    user_profile = os.path.expandvars(r"%USERPROFILE%")
    known = ["Desktop", "Downloads", "Documents", "Pictures", "Music", "Videos"]
    seen = set()
    base_paths = []
    if user_profile and Path(user_profile).exists():
        base_paths.append(Path(user_profile))
        onedrive = Path(user_profile) / "OneDrive"
        if onedrive.exists():
            base_paths.append(onedrive)
    for base in base_paths:
        for name in known:
            p = base / name
            key = str(p).lower()
            if p.exists() and key not in seen:
                roots.append((name, p))
                seen.add(key)

    for letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = Path(f"{letter}:\\")
        if drive.exists():
            roots.append((f"{letter}:\\", drive))
    return roots


def _browser_keyboard_for_roots(chat_id: str) -> str:
    buttons = []
    for label, path in _quick_roots():
        sid = _register_path(chat_id, path)
        buttons.append([{"text": label, "callback_data": f"br|open|{sid}|0"}])
    if not buttons:
        buttons.append([{"text": "No roots found", "callback_data": "br|noop"}])
    return json.dumps({"inline_keyboard": buttons})


def _truncate_label(name: str, limit: int = 48) -> str:
    if len(name) <= limit:
        return name
    return name[: limit - 3] + "..."


def _parse_file_filter(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["photo", "image", "pic", "png", "jpg", "jpeg", "webp", "gif"]):
        return "photo"
    if any(k in t for k in ["video", "mp4", "mov", "mkv", "webm"]):
        return "video"
    if any(k in t for k in ["audio", "voice", "song", "mp3", "wav", "flac", "ogg"]):
        return "audio"
    if "pdf" in t:
        return "pdf"
    if any(k in t for k in ["code", "python", ".py", "js", "ts", "java", "cpp", "c#"]):
        return "code"
    if any(k in t for k in ["text", "txt", "note", "readme", "log", "md"]):
        return "text"
    if any(k in t for k in ["doc", "document", "ppt", "xls", "csv", "office"]):
        return "doc"
    return "all"


def _file_group(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}:
        return "photo"
    if ext in {".mp4", ".mov", ".mkv", ".webm", ".avi"}:
        return "video"
    if ext in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus"}:
        return "audio"
    if ext == ".pdf":
        return "pdf"
    if ext in {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs", ".cpp", ".c", ".h", ".hpp",
        ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".kts", ".scala", ".sh", ".ps1",
        ".html", ".css", ".scss", ".sql", ".xml", ".yaml", ".yml", ".json", ".toml",
    }:
        return "code"
    if ext in {".txt", ".md", ".rst", ".log", ".ini", ".cfg", ".env"}:
        return "text"
    if ext in {".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"}:
        return "doc"
    return "other"


def _file_icon(path: Path, is_dir: bool) -> str:
    if is_dir:
        return "📁"
    group = _file_group(path)
    if group == "photo":
        return "🖼️"
    if group == "video":
        return "🎬"
    if group == "audio":
        return "🎵"
    if group == "pdf":
        return "📕"
    if group == "code":
        return "🧩"
    if group == "text":
        return "📄"
    if group == "doc":
        return "📑"
    return "📦"


def _matches_filter(path: Path, file_filter: str) -> bool:
    if file_filter == "all":
        return True
    return _file_group(path) == file_filter


def _fmt_mtime(path: Path) -> str:
    try:
        return time.strftime("%Y-%m-%d", time.localtime(path.stat().st_mtime))
    except OSError:
        return "unknown"


def _list_folder_entries(path: Path) -> tuple[list[Path], list[Path]]:
    folders = []
    files = []
    try:
        for entry in path.iterdir():
            try:
                if entry.is_dir():
                    folders.append(entry)
                elif entry.is_file():
                    files.append(entry)
            except OSError:
                continue
    except OSError:
        return [], []
    folders.sort(key=lambda p: p.name.lower())
    files.sort(key=lambda p: p.name.lower())
    return folders, files


def _browser_keyboard_for_folder(chat_id: str, folder: Path, page: int) -> str:
    file_filter, sort_mode = _get_browser_preferences(chat_id)
    folders, files = _list_folder_entries(folder)
    files = [f for f in files if _matches_filter(f, file_filter)]
    if sort_mode == "recent":
        folders.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
        files.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    else:
        folders.sort(key=lambda p: p.name.lower())
        files.sort(key=lambda p: p.name.lower())
    items = folders + files
    page_size = 12
    page = max(page, 0)
    total_pages = max((len(items) - 1) // page_size + 1, 1)
    if page >= total_pages:
        page = total_pages - 1

    start = page * page_size
    end = start + page_size
    current = items[start:end]

    keyboard = []
    parent = folder.parent if folder.parent != folder else folder
    parent_sid = _register_path(chat_id, parent)
    keyboard.append(
        [
            {"text": "Roots", "callback_data": "br|roots"},
            {"text": "Up", "callback_data": f"br|open|{parent_sid}|0"},
        ]
    )
    keyboard.append(
        [
            {"text": "Recent" if sort_mode == "recent" else "Sort:Name", "callback_data": "br|sort|recent" if sort_mode != "recent" else "br|sort|name"},
            {"text": f"Filter:{file_filter}", "callback_data": "br|noop"},
        ]
    )
    keyboard.append(
        [
            {"text": "All", "callback_data": "br|flt|all"},
            {"text": "Photo", "callback_data": "br|flt|photo"},
            {"text": "Video", "callback_data": "br|flt|video"},
        ]
    )
    keyboard.append(
        [
            {"text": "Code", "callback_data": "br|flt|code"},
            {"text": "Text", "callback_data": "br|flt|text"},
            {"text": "PDF", "callback_data": "br|flt|pdf"},
        ]
    )
    current_sid = _register_path(chat_id, folder)
    keyboard.append([{"text": "Zip+Send This Folder", "callback_data": f"br|zip|{current_sid}"}])

    for child in current:
        sid = _register_path(chat_id, child)
        if child.is_dir():
            label = f"{_file_icon(child, True)} {_truncate_label(child.name)}"
            callback_data = f"br|open|{sid}|0"
        else:
            label = f"{_file_icon(child, False)} {_truncate_label(child.name)} · {_fmt_mtime(child)}"
            callback_data = f"br|file|{sid}"
        keyboard.append([{"text": label, "callback_data": callback_data}])

    nav_row = []
    if page > 0:
        current_sid = _register_path(chat_id, folder)
        nav_row.append({"text": "Prev", "callback_data": f"br|open|{current_sid}|{page - 1}"})
    if page < total_pages - 1:
        current_sid = _register_path(chat_id, folder)
        nav_row.append({"text": "Next", "callback_data": f"br|open|{current_sid}|{page + 1}"})
    if nav_row:
        keyboard.append(nav_row)

    return json.dumps({"inline_keyboard": keyboard})


def _send_browser_roots(chat_id: str) -> None:
    file_filter, sort_mode = _get_browser_preferences(chat_id)
    text = (
        "File browser:\n"
        f"Sort: {sort_mode} | Filter: {file_filter}\n"
        "Choose a folder to continue.\n"
        "You can keep drilling down, then tap a file to send it."
    )
    _api("sendMessage", data={"chat_id": chat_id, "text": text, "reply_markup": _browser_keyboard_for_roots(chat_id)})


def _edit_browser_folder(chat_id: str, message_id: str, folder: Path, page: int = 0) -> None:
    file_filter, sort_mode = _get_browser_preferences(chat_id)
    folders, files = _list_folder_entries(folder)
    filtered_files = [f for f in files if _matches_filter(f, file_filter)]
    items_count = len(folders) + len(filtered_files)
    text = (
        f"Folder: {folder}\n"
        f"Sort: {sort_mode} | Filter: {file_filter}\n"
        f"Folders: {len(folders)} | Files: {len(filtered_files)} | Items: {items_count}"
    )
    markup = _browser_keyboard_for_folder(chat_id, folder, page)
    _api(
        "editMessageText",
        data={"chat_id": chat_id, "message_id": message_id, "text": text, "reply_markup": markup},
    )


def _handle_browser_callback(callback_query: dict) -> None:
    callback_id = str(callback_query.get("id", ""))
    data = str(callback_query.get("data", "")).strip()
    message = callback_query.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", "")).strip()
    message_id = str(message.get("message_id", "")).strip()

    if not chat_id or not message_id:
        _answer_callback(callback_id, "Browser message not found.", show_alert=True)
        return

    if data == "br|noop":
        _answer_callback(callback_id)
        return
    if data == "br|roots":
        try:
            _api(
                "editMessageText",
                data={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": "File browser roots:\nChoose a folder.",
                    "reply_markup": _browser_keyboard_for_roots(chat_id),
                },
            )
            _answer_callback(callback_id)
        except Exception:
            _answer_callback(callback_id, "Unable to load roots.", show_alert=True)
        return

    parts = data.split("|")
    if parts[0] != "br":
        _answer_callback(callback_id, "Invalid browser action.", show_alert=True)
        return

    action = parts[1]
    if action == "sort" and len(parts) >= 3:
        target_sort = "recent" if parts[2] == "recent" else "name"
        _set_browser_preferences(chat_id, sort_mode=target_sort)
        session = _get_or_create_chat_session(chat_id)
        current_sid = session.get("current_sid", "")
        current_path = _resolve_sid_path(chat_id, current_sid) if current_sid else None
        if current_path and current_path.is_dir():
            _edit_browser_folder(chat_id, message_id, current_path, 0)
        else:
            _api(
                "editMessageText",
                data={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": "File browser roots:\nChoose a folder.",
                    "reply_markup": _browser_keyboard_for_roots(chat_id),
                },
            )
        _answer_callback(callback_id, f"Sort: {target_sort}")
        return
    if action == "flt" and len(parts) >= 3:
        target_filter = parts[2]
        if target_filter not in {"all", "photo", "video", "audio", "pdf", "code", "text", "doc", "other"}:
            target_filter = "all"
        _set_browser_preferences(chat_id, file_filter=target_filter)
        session = _get_or_create_chat_session(chat_id)
        current_sid = session.get("current_sid", "")
        current_path = _resolve_sid_path(chat_id, current_sid) if current_sid else None
        if current_path and current_path.is_dir():
            _edit_browser_folder(chat_id, message_id, current_path, 0)
        else:
            _api(
                "editMessageText",
                data={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": "File browser roots:\nChoose a folder.",
                    "reply_markup": _browser_keyboard_for_roots(chat_id),
                },
            )
        _answer_callback(callback_id, f"Filter: {target_filter}")
        return
    if len(parts) < 3:
        _answer_callback(callback_id, "Invalid browser action.", show_alert=True)
        return
    sid = parts[2]
    target = _resolve_sid_path(chat_id, sid)
    if target is None:
        _answer_callback(callback_id, "Path is no longer available.", show_alert=True)
        return

    try:
        if action == "open":
            page = int(parts[3]) if len(parts) > 3 else 0
            if not target.is_dir():
                _answer_callback(callback_id, "Not a folder.", show_alert=True)
                return
            session = _get_or_create_chat_session(chat_id)
            session["current_sid"] = sid
            _edit_browser_folder(chat_id, message_id, target, page)
            _answer_callback(callback_id)
            return
        if action == "file":
            if not target.is_file():
                _answer_callback(callback_id, "Not a file.", show_alert=True)
                return
            send_file(str(target), chat_id=chat_id)
            _answer_callback(callback_id, "File sent.")
            return
        if action == "zip":
            if not target.is_dir():
                _answer_callback(callback_id, "Not a folder.", show_alert=True)
                return
            thread = threading.Thread(
                target=_send_folder_async,
                args=(str(target), chat_id, "Preparing selected folder ZIP"),
                daemon=True,
            )
            thread.start()
            _answer_callback(callback_id, "Started folder zip/send.")
            return
    except Exception:
        _answer_callback(callback_id, "Action failed.", show_alert=True)
        return

    _answer_callback(callback_id, "Unknown browser action.", show_alert=True)


def _find_file_by_name(name: str) -> Path | None:
    target = (name or "").strip().strip('"').strip("'")
    if not target:
        return None

    candidate = Path(target).expanduser()
    if candidate.exists() and candidate.is_file():
        return candidate.resolve()

    from Backend.FolderContext import get_active_folder

    roots = []
    active = (get_active_folder() or "").strip()
    if active:
        roots.append(Path(active))
    roots.append(PROJECT_ROOT)

    skip_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules", "dist", "build", ".idea", ".vscode"}
    target_lower = Path(target).name.lower()
    fallback = None
    scanned = 0

    for root in roots:
        if not root.exists() or not root.is_dir():
            continue
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for filename in files:
                scanned += 1
                if scanned > 12000:
                    return fallback
                path = Path(base) / filename
                fname = filename.lower()
                if fname == target_lower:
                    return path.resolve()
                if fallback is None and target_lower in fname:
                    fallback = path.resolve()
    return fallback


def _extract_filename_request(text: str) -> str:
    raw = (text or "").strip()
    # Quoted path/file first.
    quoted = re.search(r'["\']([^"\']+\.[A-Za-z0-9]{1,8})["\']', raw)
    if quoted:
        return quoted.group(1).strip()
    # Filename-like token.
    token = re.search(r'([A-Za-z0-9_\- .\\/:]+?\.[A-Za-z0-9]{1,8})', raw)
    if token:
        return token.group(1).strip()
    return ""


def _handle_telegram_text(chat_id: str, text: str) -> None:
    raw = (text or "").strip()
    lower = raw.lower()

    # Natural-language actions (without slash commands).
    if lower.startswith("/browse "):
        requested_filter = _parse_file_filter(raw[8:].strip())
        _set_browser_preferences(chat_id, file_filter=requested_filter, sort_mode="recent")
        _send_browser_roots(chat_id)
        return
    if any(k in lower for k in ["browse", "list files", "show files", "file browser"]) and any(
        k in lower for k in ["photo", "video", "code", "text", "pdf", "audio", "doc"]
    ):
        requested_filter = _parse_file_filter(raw)
        sort_mode = "recent" if "recent" in lower or "latest" in lower else "name"
        _set_browser_preferences(chat_id, file_filter=requested_filter, sort_mode=sort_mode)
        _send_browser_roots(chat_id)
        return
    if lower in {"browse", "browse files", "file browser", "list files", "list folders", "show files", "/browse"}:
        requested_filter = _parse_file_filter(raw)
        sort_mode = "recent" if "recent" in lower or "latest" in lower else "recent"
        _set_browser_preferences(chat_id, file_filter=requested_filter, sort_mode=sort_mode)
        _send_browser_roots(chat_id)
        return
    if lower in {"send screenshot", "take screenshot", "send screen", "send current screen"}:
        send_screenshot(chat_id=chat_id)
        return
    if lower.startswith("send me screenshot") or lower.startswith("send screenshot of"):
        send_screenshot(chat_id=chat_id)
        return
    if lower.startswith("send voice ") or lower.startswith("reply in voice "):
        parts = raw.split(" ", 2)
        payload = parts[2].strip() if len(parts) > 2 else ""
        if payload:
            send_voice_note(payload, chat_id=chat_id)
            return
    if lower.startswith("send file "):
        send_file(raw[10:].strip(), chat_id=chat_id)
        return
    if lower.startswith("send me file "):
        send_file(raw[13:].strip(), chat_id=chat_id)
        return
    if lower.startswith("send folder "):
        thread = threading.Thread(
            target=_send_folder_async,
            args=(raw[12:].strip(), chat_id, "Preparing folder ZIP"),
            daemon=True,
        )
        thread.start()
        return
    if lower.startswith("send me folder "):
        thread = threading.Thread(
            target=_send_folder_async,
            args=(raw[15:].strip(), chat_id, "Preparing folder ZIP"),
            daemon=True,
        )
        thread.start()
        return
    if lower.startswith("send me ") or lower.startswith("send "):
        candidate = raw[8:].strip() if lower.startswith("send me ") else raw[5:].strip()
        candidate_clean = candidate.strip().strip('"').strip("'")
        # If user text looks like a local path and exists, send it directly.
        if (
            "\\" in candidate_clean
            or "/" in candidate_clean
            or ":" in candidate_clean
            or Path(candidate_clean).suffix
        ):
            expanded = Path(candidate_clean).expanduser()
            if expanded.exists() and expanded.is_file():
                send_file(str(expanded.resolve()), chat_id=chat_id)
                return
        # Try resolving filename mentions like: "send me the fox.png file".
        filename_hint = _extract_filename_request(candidate_clean)
        if filename_hint:
            resolved = _find_file_by_name(filename_hint)
            if resolved:
                send_file(str(resolved), chat_id=chat_id)
                return

    if lower == "/start":
        _set_primary_chat(chat_id)
        send_text(
            "Pixie Telegram bridge connected.\n"
            "Try: /help, /screenshot, /sendfile <absolute_path>, or ask normal questions.",
            chat_id=chat_id,
        )
        return
    if lower == "/help":
        send_text(
            "Commands:\n"
            "/screenshot\n"
            "/sendfile <absolute_path>\n"
            "/sendfolder <absolute_folder_path>\n"
            "/voice <text>\n"
            "/browse [photo|video|code|text|pdf]\n"
            "Any other text = ask Pixie",
            chat_id=chat_id,
        )
        return
    if lower.startswith("/screenshot"):
        send_screenshot(chat_id=chat_id)
        return
    if lower.startswith("/sendfile "):
        send_file(text[10:].strip(), chat_id=chat_id)
        return
    if lower.startswith("/sendfolder "):
        thread = threading.Thread(
            target=_send_folder_async,
            args=(text[12:].strip(), chat_id, "Preparing folder ZIP"),
            daemon=True,
        )
        thread.start()
        return
    if lower.startswith("/voice "):
        send_voice_note(text[7:].strip(), chat_id=chat_id)
        return

    reply = _reply_with_pixie(text)
    send_text(reply, chat_id=chat_id)


def _handle_update(update: dict) -> None:
    callback_query = update.get("callback_query")
    if callback_query:
        message = callback_query.get("message") or {}
        chat = message.get("chat") or {}
        chat_id = str(chat.get("id", "")).strip()
        if chat_id and _allowed_chat(chat_id):
            _handle_browser_callback(callback_query)
        return

    message = update.get("message") or update.get("edited_message") or {}
    if not message:
        return
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id", "")).strip()
    if not chat_id or not _allowed_chat(chat_id):
        return

    _set_primary_chat(chat_id)

    if "text" in message and message["text"]:
        _handle_telegram_text(chat_id, message["text"])
        return

    if "voice" in message and message["voice"]:
        voice = message["voice"]
        file_id = voice.get("file_id")
        if not file_id:
            send_text("Voice message received, but file id was missing.", chat_id=chat_id)
            return
        local_audio = _download_telegram_file(file_id, suffix=".ogg")
        transcript = _transcribe_ogg(local_audio)
        if transcript:
            answer = _reply_with_pixie(transcript)
            send_voice_note(answer, chat_id=chat_id)
            send_text(f"Transcript: {transcript}", chat_id=chat_id)
        else:
            send_voice_note("I received your voice message. Please add Groq API key for transcription.", chat_id=chat_id)
        return

    send_text("Supported: text and voice messages.", chat_id=chat_id)


def _poll_loop() -> None:
    if not TELEGRAM_TOKEN:
        return
    state = _load_state()
    offset = int(state.get("last_update_id", 0)) + 1

    while True:
        try:
            resp = requests.get(
                f"{BASE_URL}/getUpdates",
                params={"timeout": 50, "offset": offset},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                time.sleep(2)
                continue

            updates = data.get("result", [])
            for upd in updates:
                update_id = upd.get("update_id", 0)
                if update_id >= offset:
                    offset = update_id + 1
                    state["last_update_id"] = update_id
                    _save_state(state)
                try:
                    _handle_update(upd)
                except Exception:
                    pass
        except Exception:
            time.sleep(2)


def start_telegram_service() -> str:
    global _service_started
    if not TELEGRAM_TOKEN:
        return "Telegram disabled: missing TELEGRAM_BOT_TOKEN."
    with _service_lock:
        if _service_started:
            return "Telegram service already running."
        thread = threading.Thread(target=_poll_loop, daemon=True)
        thread.start()
        _service_started = True
    return "Telegram service started."
