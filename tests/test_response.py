import pytest

# test where
from src.quickbase_json.qb_response import QBResponse
from src.quickbase_json.helpers import Where, IncorrectParameters
from tests import sample_data


# test loading in data
@pytest.mark.parametrize('data, expected', [
    (sample_data.record_data, sample_data.record_data_load)
])
def test_load(data, expected):
    assert QBResponse('records', sample_data=data) == expected


# test getting info, basic tests, does not test formatting
def test_get_info():
    assert "{'6': {'value': 'Andre Harris'}, '7': {'value': 10}, '8': {'value': '2019-12-18T08:00:00.000Z'}}" in QBResponse('records', sample_data=sample_data.record_data).info(prt=False)
