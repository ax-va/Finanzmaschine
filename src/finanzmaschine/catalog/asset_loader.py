import yaml

from pathlib import Path
from typing import List

from finanzmaschine.catalog import asset_registry
from finanzmaschine.core import assets as assets_module
from finanzmaschine.core.assets.asset import A


def load_assets(dir_path: Path) -> List[A]:
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
                asset_type_str = None
                kwargs = {"id": key}
                for attr_key, attr_val in metadata.items():
                    if isinstance(attr_val, dict):
                        kwargs[attr_key] = asset_registry.get(attr_val.get("id"))
                    else:
                        if attr_key == "type":
                            asset_type_str = attr_val[0].upper() + attr_val[1:].lower()
                        else:
                            kwargs[attr_key] = attr_val

                asset_type = getattr(assets_module, asset_type_str)
                asset = asset_type(**kwargs)
                assets.append(asset)

    return assets
