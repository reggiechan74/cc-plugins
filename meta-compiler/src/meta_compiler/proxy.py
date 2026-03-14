"""Data-backed symbol proxy with access logging.

In v2, proxies hold real data (from fixtures) and return actual values
on __getitem__. Each access logs the symbol name for orphan/phantom detection.
"""

from __future__ import annotations


class SymbolProxy:
    """Proxy for a registered symbol backed by fixture data."""

    def __init__(self, name: str, data: dict | None, access_log: set):
        self.name = name
        self._data = data
        self._access_log = access_log

    def __getitem__(self, key):
        self._access_log.add(self.name)
        if self._data is None:
            raise RuntimeError(
                f"No fixture data for symbol '{self.name}'. "
                f"Add a python:fixture block with data for '{self.name}'."
            )
        return self._data[key]

    def __repr__(self):
        backed = "data-backed" if self._data is not None else "no-data"
        return f"SymbolProxy({self.name!r}, {backed})"
