"""
file_search.py — find files on the PC by name (partial match), fast, no index
needed for typical home-folder sized searches.
"""
from pathlib import Path


def find_files(name_fragment: str, search_root: str = None, limit: int = 20) -> list:
    root = Path(search_root).expanduser() if search_root else Path.home()
    name_fragment = name_fragment.lower()
    matches = []
    for p in root.rglob("*"):
        try:
            if name_fragment in p.name.lower():
                matches.append(str(p))
                if len(matches) >= limit:
                    break
        except PermissionError:
            continue
    return matches


if __name__ == "__main__":
    print(find_files("resume"))
