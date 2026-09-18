"""
file_organizer.py — sorts a messy folder (e.g. Downloads) into subfolders by type.
"""

import shutil
from pathlib import Path

CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".csv"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".webm"],
    "Audio": [".mp3", ".wav", ".m4a", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Installers": [".exe", ".msi", ".dmg", ".deb", ".appimage"],
    "Code": [".py", ".js", ".html", ".css", ".json", ".ipynb", ".java", ".cpp"],
}


def organize(folder_path: str) -> dict:
    """Move files in folder_path into category subfolders. Returns a summary dict."""
    folder = Path(folder_path).expanduser()
    if not folder.is_dir():
        return {"error": f"Not a folder: {folder}"}

    moved = {cat: 0 for cat in CATEGORIES}
    moved["Other"] = 0

    for item in folder.iterdir():
        if item.is_dir():
            continue
        ext = item.suffix.lower()
        target_cat = "Other"
        for cat, exts in CATEGORIES.items():
            if ext in exts:
                target_cat = cat
                break
        target_dir = folder / target_cat
        target_dir.mkdir(exist_ok=True)
        try:
            shutil.move(str(item), str(target_dir / item.name))
            moved[target_cat] += 1
        except shutil.Error:
            pass  # file with same name already exists there; skip rather than overwrite

    return moved


def rename_file(path: str, new_name: str) -> str:
    """Rename a single file or folder in place. new_name is just the name
    (no path) — keeps it in the same directory."""
    p = Path(path).expanduser()
    if not p.exists():
        return f"Not found: {p}"
    target = p.parent / new_name
    if target.exists():
        return f"A file named '{new_name}' already exists there."
    p.rename(target)
    return f"Renamed to: {target}"


def move_file(path: str, destination_folder: str) -> str:
    """Move a file or folder to a different location (change its folder)."""
    p = Path(path).expanduser()
    dest = Path(destination_folder).expanduser()
    if not p.exists():
        return f"Not found: {p}"
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / p.name
    if target.exists():
        return f"A file named '{p.name}' already exists in {dest}."
    shutil.move(str(p), str(target))
    return f"Moved to: {target}"


def _peek_content(path: Path, max_chars: int = 1500) -> str:
    """Best-effort content preview for the rename-by-content feature.
    Text-like files are read directly; images go through OCR (vision.py);
    anything else falls back to just the filename/extension."""
    ext = path.suffix.lower()
    text_exts = {".txt", ".md", ".py", ".csv", ".json", ".log", ".html", ".css", ".js"}
    image_exts = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
    try:
        if ext in text_exts:
            return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
        if ext in image_exts:
            from modules import vision
            return vision.read_text_from_image(str(path))[:max_chars]
    except Exception as e:
        return f"(couldn't read content: {e})"
    return f"(binary file, extension {ext}, no text preview available)"


def suggest_name_from_content(path: str, ask_fn) -> dict:
    """Reads a file's actual content and asks the AI brain for a clearer,
    descriptive filename. Returns a suggestion WITHOUT renaming anything —
    renaming based on an AI guess without the user seeing it first is the
    kind of automation that quietly loses files; the caller (dashboard/CLI)
    shows the suggestion and only calls rename_file() if the user confirms.
    """
    p = Path(path).expanduser()
    if not p.exists():
        return {"error": f"Not found: {p}"}
    content = _peek_content(p)
    prompt = (
        f"A file named '{p.name}' contains this content:\n\n{content}\n\n"
        f"Suggest ONE better, descriptive filename for it (keep the same '{p.suffix}' extension). "
        "Reply with ONLY the filename, nothing else — no explanation, no quotes."
    )
    suggestion = ask_fn(prompt).strip().strip('"').strip("'")
    if not suggestion.endswith(p.suffix) and p.suffix:
        suggestion += p.suffix
    return {"original": p.name, "suggested": suggestion, "path": str(p)}


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "Downloads")
    print(organize(path))
