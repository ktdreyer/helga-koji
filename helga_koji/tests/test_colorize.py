from helga_koji import colorize
import pytest


TASKS = [
    ('FREE', '\x0306FREE\x03'),
    ('OPEN', '\x0307OPEN\x03'),
    ('CLOSED', '\x0303CLOSED\x03'),
    ('CANCELED', '\x0305CANCELED\x03'),
    ('FAILED', '\x0304FAILED\x03'),
]


@pytest.mark.parametrize('state_name,expected', TASKS)
def test_colorize_task_state(state_name, expected):
    result = colorize.task_state(state_name)
    assert result == expected


BUILDS = [
    ('BUILDING', '\x0302BUILDING\x03'),
    ('COMPLETE', '\x0303COMPLETE\x03'),
    ('DELETED', '\x0305DELETED\x03'),
    ('FAILED', '\x0304FAILED\x03'),
    ('CANCELED', '\x0307CANCELED\x03'),
]


@pytest.mark.parametrize('state_name,expected', BUILDS)
def test_colorize_build_state(state_name, expected):
    result = colorize.build_state(state_name)
    assert result == expected
