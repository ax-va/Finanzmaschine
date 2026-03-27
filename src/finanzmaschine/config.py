from dataclasses import dataclass

import yaml
from pathlib import Path
from finanzmaschine import SETTINGS_PATH


@dataclass
class Paths:
    data: Path


@dataclass
class Settings:
    paths: Paths


def load_settings(settings_path: str | Path = None) -> Settings:
    if settings_path is None:
        settings_path = SETTINGS_PATH

    with open(settings_path) as f:
        data = yaml.safe_load(f)

    return Settings(
        paths=Paths(
            data=Path(data["paths"]["data"]),
        ),
    )


SETTINGS = load_settings()
DATA_DIR: Path = SETTINGS.paths.data
