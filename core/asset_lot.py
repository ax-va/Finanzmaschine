from lot import Lot


class AssetLot(Lot):
    def __init__(self, asset_name: str = None):
        self.name = asset_name
        super().__init__()