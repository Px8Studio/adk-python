"""
Wrapper module for DNB Statistics API client.

This module provides a Python-importable interface to the Kiota-generated
DNB Statistics client, working around the hyphenated directory name limitation.

The wrapper uses importlib to dynamically load the client package, ensuring
that relative imports within the generated code work correctly.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

# Path to the dnb-statistics directory
_client_dir = Path(__file__).parent / "dnb-statistics"
_client_file = _client_dir / "dnb_statistics_client.py"

# Create a package namespace for the client
_package_name = "dnb_statistics_pkg"

# Load the client module as part of a package
def _load_client() -> ModuleType:
    """Load the DNB Statistics client module with proper package context."""
    # Add parent to sys.modules as a package
    if _package_name not in sys.modules:
        package = ModuleType(_package_name)
        package.__path__ = [str(_client_dir)]
        package.__file__ = str(_client_dir / "__init__.py")
        sys.modules[_package_name] = package
    
    # Load the client module within the package
    module_name = f"{_package_name}.dnb_statistics_client"
    if module_name not in sys.modules:
        spec = importlib.util.spec_from_file_location(module_name, _client_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            module.__package__ = _package_name
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
    return sys.modules[module_name]

# Load and extract the client class
_module = _load_client()
DnbStatisticsClient = _module.DnbStatisticsClient

__all__ = ["DnbStatisticsClient"]
