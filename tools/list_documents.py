from pathlib import Path

def list_documents(base_dir: str = "examples", allowed_ext: tuple[str, ...] = (".txt", ".md")) -> list[str]:
    root = Path(base_dir)
    files = []
    for path in root.iterdir():
        if path.is_file() and path.suffix.lower() in allowed_ext:
            files.append(path.name)
    return sorted(files)
