import time

from common.utilities import pretty_time_delta, timeit


@timeit
def _wait_500ms() -> None:
    time.sleep(0.5)


def test_timeit(caplog):
    _wait_500ms()
    assert "Function _wait_500ms executed" in caplog.text


def test_pretty_time_delta():
    assert pretty_time_delta(0.5) == "0(days) 00:00:00.5000000"
    assert pretty_time_delta(12.632) == "0(days) 00:00:12.6319999"
