import datetime
import sys

import pytest

# test where
import os
from src.quickbase_json.qb_response import QBQueryResponse
from tests import sample_data
from copy import deepcopy


# test loading in data
@pytest.mark.parametrize('data, expected', [
    (sample_data.record_data, sample_data.record_data_load)
])
def test_load(data, expected):
    assert QBQueryResponse(sample_data=data) == expected


# test getting info, basic tests, does not test formatting
def test_get_info():
    assert "{'6': {'value': 'Andre Harris'}, '7': {'value': 10.0}, '8': {'value': '2019-12-18T08:00:00.000Z'}}" in QBQueryResponse(
        sample_data=sample_data.record_data.copy()).info(prt=False)


# test getting info, basic tests, does not test formatting
def test_denest():
    res = QBQueryResponse(sample_data=deepcopy(sample_data.record_data))
    res.denest()
    assert res.data() == [{'8': '2019-12-18T08:00:00.000Z', '6': 'Andre Harris', '7': 10}]


# test datetime convert
def test_convert_datetime():
    # test datetime convert w/o denest
    res = QBQueryResponse(sample_data=deepcopy(sample_data.record_data))
    res.convert_type('datetime')
    dt_test = res.data()[0].get('8').get('value')

    # test datetime convert w/ denest
    res2 = QBQueryResponse('records', sample_data=deepcopy(sample_data.record_data))
    res2.denest()
    res2.convert_type('datetime')
    dt_test2 = res2.data()[0].get('8')

    # make sure both are datetime
    assert isinstance(dt_test, datetime.datetime)
    assert isinstance(dt_test2, datetime.datetime)


# test currency convert
def test_convert_currency():
    # test datetime convert w/o denest
    res = QBQueryResponse('records', sample_data=deepcopy(sample_data.record_data_currency))
    res.convert_type('numeric currency', fmt='$')
    res.denest()

    # make sure both are formatted correctly
    assert res.data()[0].get('6') == '$55.55'
    assert res.data()[1].get('6') == '$13.00'


# test datetime convert
def test_round_ints():
    # test converting ints with floating point
    res = QBQueryResponse('records', sample_data=deepcopy(sample_data.record_data))

    # assert float, then int
    assert type(res.data()[0].get('7').get('value')) == float
    res.round_ints()
    assert type(res.data()[0].get('7').get('value')) == int


def test_operations():
    res = QBQueryResponse('records', sample_data=sample_data.record_data)
    assert res.operations == []
    res.denest()
    assert res.operations == ['denest']
    res.orient('records', key=6)
    assert res.operations == ['denest', 'orient']
