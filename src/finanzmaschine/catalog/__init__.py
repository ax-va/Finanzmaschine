import pkgutil
import importlib

from .instrument_registry import InstrumentRegistry

registry = InstrumentRegistry()


def _import_submodules(package_name: str) -> None:
    package = importlib.import_module(package_name)

    for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        importlib.import_module(module_name)


_import_submodules(__name__)
