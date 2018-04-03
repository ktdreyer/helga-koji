import pytest
from helga_productpages.actions.release_date import match


values = [
    ('helga: RHCS 3.1 release date', 'ceph-3-1'),
    ('helga: RHCS 3.1 ga date', 'ceph-3-1'),
    ('helga: RHEL 7 release date', 'rhel-7-0'),
    ('helga: rhel 8 release date', 'rhel-8-0'),
    ('helga: osp 13 release date', 'rhosp-13.0'),
    ('helga: osp 13 date', 'rhosp-13.0'),
    ('helga: rhcs 3.0 z2 date', 'ceph-3-0'),
    ('helga: rhcs 3.0 z2 date?', 'ceph-3-0'),
]


@pytest.mark.parametrize('test_input,expected', values)
def test_match(test_input, expected):
    result = match(test_input)
    assert result.shortname == expected
