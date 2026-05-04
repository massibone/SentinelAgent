from pathlib import Path

def read_document(filename: str, base_dir: str = "examples") -> str:
    path = (Path(base_dir) / filename).resolve()
    base = Path(base_dir).resolve()

    if not str(path).startswith(str(base)):
        raise PermissionError("Accesso fuori dalla directory consentita")

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File non trovato: {filename}")

    return path.read_text(encoding="utf-8")
