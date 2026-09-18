"""Negative / security-adjacent checks: the API must refuse what it should refuse."""
import pytest
import requests

from api.booking_client import BookingClient
from config import API_URL
from conftest import future_dates

pytestmark = pytest.mark.api


def test_login_rejects_bad_credentials():
    r = requests.post(f"{API_URL}/auth/login", json={"username": "admin", "password": "wrong"})
    assert r.status_code == 401
    assert "token" not in r.text


@pytest.mark.parametrize("token", [None, "not-a-real-token"], ids=["no-token", "bogus-token"])
@pytest.mark.parametrize("verb", ["get", "update", "delete"])
def test_protected_endpoints_reject_unauthenticated(booking, verb, token):
    anon = BookingClient(auth=False)
    if token:
        anon.set_token(token)
    call = {
        "get": lambda: anon.get_booking(booking["bookingid"]),
        "update": lambda: anon.update_booking(booking["bookingid"], {**booking, "lastname": "Pwned"}),
        "delete": lambda: anon.delete_booking(booking["bookingid"]),
    }[verb]
    assert call().status_code == 403


def test_unauthenticated_delete_leaves_booking_intact(api_client, booking):
    BookingClient(auth=False).delete_booking(booking["bookingid"])
    assert api_client.get_booking(booking["bookingid"]).status_code == 200


def test_client_supplied_booking_id_is_ignored(api_client):
    """Mass-assignment: posting bookingid=1 must not overwrite booking 1."""
    before = api_client.get_booking(1).json()
    checkin, checkout = future_dates()
    r = api_client.create_booking({**BookingClient.payload(1, checkin, checkout, "Inject", "Tester"), "bookingid": 1})
    assert r.status_code == 201
    new_id = r.json()["bookingid"]
    assert new_id != 1
    assert api_client.get_booking(1).json() == before
    api_client.delete_booking(new_id)
