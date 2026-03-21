"""Tests for scalar reference collection in checks.py."""
from meta_compiler.checks import collect_scalar_refs


def test_collect_scalar_refs_finds_matching_names():
    source = "Expression('t_eff', definition=lambda: H - M * beta)"
    scalar_names = {"H", "M", "beta"}
    access_log = set()
    collect_scalar_refs(source, scalar_names, access_log)
    assert access_log == {"H", "M", "beta"}


def test_collect_scalar_refs_ignores_non_scalar_names():
    source = "Expression('cost', definition=lambda: cap[i] + overhead)"
    scalar_names = {"overhead"}
    access_log = set()
    collect_scalar_refs(source, scalar_names, access_log)
    assert access_log == {"overhead"}
    assert "cap" not in access_log


def test_collect_scalar_refs_handles_empty_scalars():
    source = "Parameter('cap', index='W')"
    scalar_names = set()
    access_log = set()
    collect_scalar_refs(source, scalar_names, access_log)
    assert access_log == set()


def test_collect_scalar_refs_no_false_positives_from_substrings():
    """'capacity' should not match scalar 'cap'."""
    source = "capacity = 100"
    scalar_names = {"cap"}
    access_log = set()
    collect_scalar_refs(source, scalar_names, access_log)
    assert access_log == set()
