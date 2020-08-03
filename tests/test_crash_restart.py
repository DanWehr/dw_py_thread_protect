from .. import crash_restart
import unittest.mock as mock


def simple_add(val):
    return 1 + val


def test_valid_run_simple():
    @crash_restart.crash_restart(rerun_delay=1)
    def simple_add(val):
        return 1 + val

    assert simple_add(2) == 3


def test_valid_run():
    before_mock = mock.Mock()
    after_mock = mock.Mock()
    exc_mock = mock.Mock()

    @crash_restart.crash_restart(rerun_delay=1, before_func=before_mock, after_func=after_mock, exc_func=exc_mock)
    def simple_add(val):
        return 1 + val

    assert simple_add(2) == 3
    assert before_mock.called
    assert before_mock.call_count == 1
    assert after_mock.called
    assert after_mock.call_count == 1
    assert not exc_mock.called
    assert exc_mock.call_count == 0
