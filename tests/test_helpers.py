import sys

import pytest

# test where
import os
import os
from quickbase_json.helpers import Where, IncorrectParameters


@pytest.mark.parametrize('fid, operator, value, expected', [
    (3, 'EX', 12345, '{3.EX.12345}'),
    (3, 'XEX', 12345, '{3.XEX.12345}'),
    (10, 'EX', 12345, '{10.EX.12345}')
])
def test_where(fid, operator, value, expected):
    assert Where(fid, operator, value).build() == expected


@pytest.mark.parametrize('fid, operator, value, expected', [
    (3, 'EX', [1, 2, 3, 4, 5], '{3.EX.1}OR{3.EX.2}OR{3.EX.3}OR{3.EX.4}OR{3.EX.5}'),
    (3, 'EX', [1], '{3.EX.1}')
])
def test_where_join(fid, operator, value, expected):
    assert Where(fid, operator, value).build(join='OR') == expected


# test invalid parameters, given to where
def test_invalid_params():
    with pytest.raises(IncorrectParameters):
        Where(3, 'EX', 12345).build(join='OR')
