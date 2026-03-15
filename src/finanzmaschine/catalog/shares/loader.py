import yaml

from pathlib import Path
from typing import List

from finanzmaschine.catalog.asset_enum import parse_asset
from finanzmaschine.core.market.share import Share


def load_shares(dir_path: Path) -> List[Share]:
    shares = []
    share_def_files = sorted(dir_path.rglob("*.y*ml"))
    for share_def_file in share_def_files:
        with share_def_file.open() as f:
            data = yaml.safe_load(f) or {}

            if not isinstance(data, dict):
                raise ValueError(f"Invalid YAML structure in {share_def_file!r}")

            for isin, metadata in data.items():

                if not isinstance(metadata, dict):
                    raise ValueError(f"Invalid YAML structure in {share_def_file!r}")

                name = metadata.get("name")
                if name is None:
                    raise ValueError(f"Name missing for ISIN {isin!r}")

                asset_str = metadata.get("asset")
                if asset_str is None:
                    raise ValueError(f"Asset missing for ISIN {isin!r}")

                asset = parse_asset(asset_str)
                share = Share(
                    isin=isin,
                    name=name,
                    asset=asset,
                )
                shares.append(share)

    return shares
