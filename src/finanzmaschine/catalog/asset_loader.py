import yaml

from pathlib import Path
from typing import List

from finanzmaschine.catalog.asset_registry import asset_registry
from finanzmaschine.portfolio.assets.base_asset import BaseAsset
from finanzmaschine.utils.path_helper import ensure_path


def load_assets[A: BaseAsset](path: Path, asset_type: type[A]) -> List[A]:

    path = ensure_path(path)
    if path.is_dir():
        asset_def_files = sorted(path.rglob("*.y*ml"))
    else:
        asset_def_files = (path, ) if path.suffix.lower() in {".yml", ".yaml"} else ()

    if not asset_def_files:
        raise ValueError(f"YAML files not found: {str(path)!r}")

    assets = []
    for asset_def_file in asset_def_files:
        with asset_def_file.open() as f:
            # YAML dictionary
            data = yaml.safe_load(f) or {}
            if not isinstance(data, dict):
                raise ValueError(f"Invalid YAML structure: {str(asset_def_file)!r}")

            # metadata dictionary
            for key, metadata in data.items():
                if not isinstance(metadata, dict):
                    raise ValueError(f"Invalid YAML structure: {str(asset_def_file)!r}")

                # metadata attributes
                kwargs = {"id": key}
                for attr_key, attr_val in metadata.items():
                    if isinstance(attr_val, dict):
                        # for example, attr_key="underlying_asset"
                        kwargs[attr_key] = asset_registry.get(attr_val["id"])
                    else:
                        kwargs[attr_key] = attr_val

                asset = asset_type(**kwargs)
                assets.append(asset)

    return assets
