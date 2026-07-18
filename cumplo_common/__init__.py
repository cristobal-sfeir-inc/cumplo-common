"""A one-stop library that centralizes the core logic and protects the domain of the Cumplo API project."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cumplo-common")
except PackageNotFoundError:  # not installed (e.g. raw source checkout)
    __version__ = "0.0.0"
