import yaml

from pathlib import Path
from typing import List

from finanzmaschine.catalog.asset_enum import parse_asset
from finanzmaschine.core.market.etp import Etp


def load_etps(dir_path: Path) -> List[Etp]:
    etps = []
    etp_def_files = sorted(dir_path.rglob("*.y*ml"))
    for etp_def_file in etp_def_files:
        with etp_def_file.open() as f:
            data = yaml.safe_load(f) or {}
            if not isinstance(data, dict):
                raise ValueError(f"Invalid YAML structure in {etp_def_file!r}")

            for isin, metadata in data.items():
                if not isinstance(metadata, dict):
                    raise ValueError(f"Invalid YAML structure in {etp_def_file!r}")

                name = metadata.get("name")
                if name is None:
                    raise ValueError(f"Name missing for ISIN {isin!r}")

                underlying_str = metadata.get("underlying")
                if underlying_str is None:
                    raise ValueError(f"Asset missing for ISIN {isin!r}")

                underlying = parse_asset(underlying_str)
                etp = Etp(
                    isin=isin,
                    name=name,
                    underlying=underlying,
                )
                etps.append(etp)

    return etps
