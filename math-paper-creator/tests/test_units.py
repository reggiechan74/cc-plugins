from meta_compiler.units import Unit, parse_unit, units_compatible, units_multiply, units_divide


def test_base_unit():
    u = parse_unit("hours")
    assert u == Unit(numer=("hours",), denom=())


def test_compound_unit():
    u = parse_unit("hours/headcount")
    assert u == Unit(numer=("hours",), denom=("headcount",))


def test_dimensionless():
    u = parse_unit("dimensionless")
    assert u == Unit(numer=(), denom=())


def test_compatible_same():
    assert units_compatible(parse_unit("hours"), parse_unit("hours"))


def test_incompatible():
    assert not units_compatible(parse_unit("hours"), parse_unit("headcount"))


def test_dimensionless_compatible_with_self():
    assert units_compatible(parse_unit("dimensionless"), parse_unit("dimensionless"))


def test_multiply_units():
    # dimensionless * hours = hours
    result = units_multiply(parse_unit("dimensionless"), parse_unit("hours"))
    assert result == parse_unit("hours")


def test_multiply_compound():
    # hours/headcount * headcount = hours
    result = units_multiply(parse_unit("hours/headcount"), parse_unit("headcount"))
    assert result == parse_unit("hours")


def test_multiply_two_base():
    # hours * dollars = hours*dollars (compound numer)
    result = units_multiply(parse_unit("hours"), parse_unit("dollars"))
    assert units_compatible(result, Unit(numer=("dollars", "hours"), denom=()))


def test_divide_units():
    # hours / headcount = hours/headcount
    result = units_divide(parse_unit("hours"), parse_unit("headcount"))
    assert result == parse_unit("hours/headcount")


def test_divide_cancel():
    # hours / hours = dimensionless
    result = units_divide(parse_unit("hours"), parse_unit("hours"))
    assert result == parse_unit("dimensionless")


def test_unit_str():
    assert str(parse_unit("hours")) == "hours"
    assert str(parse_unit("dimensionless")) == "dimensionless"
    assert str(parse_unit("hours/headcount")) == "hours/headcount"
