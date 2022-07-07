import pytest

# test where

from quickbase_json.auth import QBUser


def test_qb_user():
    user = QBUser(realm='test', username='test@username.com')
    r = user.authenticate(password='test#pass', hours=24)
    assert r.ok is False
