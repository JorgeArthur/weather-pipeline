from validate import find_bad_temperatures


def make_row(temp):
    return {"city": "london", "temperature_c": temp}


def test_normal_temperature_is_ok():
    assert find_bad_temperatures([make_row(15.0)]) == []


def test_too_hot_is_flagged():
    rows = [make_row(15.0), make_row(999.0)]
    assert find_bad_temperatures(rows) == [make_row(999.0)]


def test_none_is_not_flagged():
    assert find_bad_temperatures([make_row(None)]) == []