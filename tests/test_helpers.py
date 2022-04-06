import sys

import pytest

# test where
import os
import os

from src.quickbase_json import QBClient
from src.quickbase_json.helpers import Where, IncorrectParameters, FileUpload

print(os.getcwd())


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


# test file helper
def test_file_upload():
    result = open('tests/test_assets/fileupload_result.txt', 'r').readline()
    assert str(FileUpload(path='tests/test_assets/140.jpeg')) == str(result)


# test where being properly converted during use in Query
def test_where_in_query():
    qbc = QBClient(realm='', auth='')
    q = qbc.query_records(table='', select=[], where=Where(3, 'EX', 1337), _test_=True)
    assert str(q) == "{'from': '', 'select': [], 'where': '{3.EX.1337}'}"
