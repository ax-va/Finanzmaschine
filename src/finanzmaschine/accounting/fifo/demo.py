import polars as pl

from finanzmaschine import PROJECT_ROOT
from finanzmaschine.config import SETTINGS

PRIVATE_DIR = PROJECT_ROOT / SETTINGS.paths.private

df = (
    pl.read_csv(
        PRIVATE_DIR / "etp.csv",
        try_parse_dates=True,
    ).sort("datetime")
)
pl.Config.set_tbl_rows(-1)
pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_width_chars(200)
print(df)