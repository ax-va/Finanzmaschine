from pathlib import Path


def ensure_path(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Path {path!r} does not exist")

    return path


def ensure_directory(path: Path) -> Path:
    ensure_path(path)
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path!r}")

    return path
