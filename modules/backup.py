"""
backup.py — zips specified folders (e.g. code repos) and copies them to a
backup destination (another local/external drive, or a synced cloud folder
like Google Drive/OneDrive's local sync folder — this script doesn't talk to
cloud APIs directly, it just drops the zip into a folder that your existing
cloud-sync app watches, which is simpler and more reliable than reimplementing
cloud upload).
"""

import shutil
from datetime import datetime
from pathlib import Path


def backup_folder(source_path: str, destination_dir: str) -> str:
    source = Path(source_path).expanduser()
    dest_dir = Path(destination_dir).expanduser()
    dest_dir.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        return f"Source not found: {source}"

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_name = f"{source.name}-backup-{stamp}"
    archive_path = shutil.make_archive(str(dest_dir / archive_name), "zip", root_dir=str(source))
    return archive_path


def backup_multiple(sources: list, destination_dir: str) -> list:
    return [backup_folder(s, destination_dir) for s in sources]


if __name__ == "__main__":
    print(backup_folder(".", "~/GyrusBackups"))
