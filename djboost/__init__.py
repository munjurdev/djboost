from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("djboost")
except PackageNotFoundError:
    __version__ = "0.8.0"
