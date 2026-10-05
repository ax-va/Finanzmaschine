from pathlib import Path


def ensure_path(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Path {str(path)!r} does not exist")
    return path


def ensure_directory(dir_path: Path) -> Path:
    ensure_path(dir_path)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {str(dir_path)!r}")
    return dir_path
