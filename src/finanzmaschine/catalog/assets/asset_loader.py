import yaml

from pathlib import Path
from typing import List

from finanzmaschine.core.assets.asset import Asset


def load_assets(dir_path: Path) -> List[Asset]:
    assets = []
    asset_def_files = sorted(dir_path.rglob("*.y*ml"))
    for asset_def_file in asset_def_files:
        with asset_def_file.open() as f:
            data = yaml.safe_load(f) or {}
            if not isinstance(data, dict):
                raise ValueError(f"Invalid YAML structure in {asset_def_file!r}")

            for key, metadata in data.items():
                if not isinstance(metadata, dict):
                    raise ValueError(f"Invalid YAML structure in {asset_def_file!r}")

                name = metadata.get("name")
                if name is None:
                    raise ValueError(f"Name missing for {key!r}")

                etp = Asset(
                    id=key,
                    name=name,
                )
                assets.append(etp)

    return assets
