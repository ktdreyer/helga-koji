from datetime import timedelta
import pytest
from helga_koji.util import describe_delta

TESTS = [
    (3.14159, '0 min 3 secs'),
    (5,       '0 min 5 secs'),
    (5.9,     '0 min 5 secs'),
    (60,      '1 min 0 secs'),
    (3600,    '1 hr 0 min'),
]


@pytest.mark.parametrize('seconds,expected', TESTS)
def test_describe_delta(seconds, expected):
    delta = timedelta(seconds=seconds)
    result = describe_delta(delta)
    assert result == expected
