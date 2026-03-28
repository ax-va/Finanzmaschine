import yaml

from pathlib import Path
from typing import List

from finanzmaschine.catalog import asset_registry
from finanzmaschine.portfolio.assets.base_asset import BaseAsset


def load_assets[A: BaseAsset](dir_path: Path, asset_type: type[A]) -> List[A]:
    assets = []
    asset_def_files = sorted(dir_path.rglob("*.y*ml"))
    for asset_def_file in asset_def_files:
        with asset_def_file.open() as f:
            # YAML dictionary
            data = yaml.safe_load(f) or {}
            if not isinstance(data, dict):
                raise ValueError(f"Invalid YAML structure in {asset_def_file!r}")

            # metadata dictionary
            for key, metadata in data.items():
                if not isinstance(metadata, dict):
                    raise ValueError(f"Invalid YAML structure in {asset_def_file!r}")

                # metadata attributes
                kwargs = {"id": key}
                for attr_key, attr_val in metadata.items():
                    if isinstance(attr_val, dict):
                        kwargs[attr_key] = asset_registry.get(attr_val.get("id"))
                    else:
                        kwargs[attr_key] = attr_val

                asset = asset_type(**kwargs)
                assets.append(asset)

    return assets
