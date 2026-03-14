import pytest


@pytest.fixture(autouse=True)
def fresh_registry():
    """Reset the global registry before each test."""
    from meta_compiler.registry import registry
    registry.reset()
    yield registry
