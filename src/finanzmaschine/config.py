from dataclasses import dataclass

import yaml
from pathlib import Path
from finanzmaschine import SETTINGS_PATH, PROJECT_ROOT


@dataclass
class Paths:
    private_data: Path


@dataclass
class Settings:
    paths: Paths


def load_settings(settings_path: str | Path = None) -> Settings:
    if settings_path is None:
        settings_path = SETTINGS_PATH

    with open(settings_path) as f:
        data = yaml.safe_load(f)

    return Settings(
        paths=Paths(private_data=Path(data["paths"]["private_data"])),
    )


SETTINGS = load_settings()
PRIVATE_DATA_DIR = PROJECT_ROOT / SETTINGS.paths.private_data
