from dataclasses import dataclass

import yaml
from pathlib import Path
from finanzmaschine import SETTINGS_PATH


@dataclass
class Paths:
    private: str


@dataclass
class Settings:
    paths: Paths


def load_settings(settings_path: str | Path = None) -> Settings:
    if settings_path is None:
        settings_path = SETTINGS_PATH

    with open(settings_path) as f:
        data = yaml.safe_load(f)

    return Settings(
        paths=Paths(**data["paths"]),
    )


SETTINGS = load_settings()
