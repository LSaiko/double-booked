import pytest

from api.booking_client import BookingClient
from conftest import future_dates

pytestmark = pytest.mark.api


@pytest.mark.parametrize("roomid, nights, first, last", [
    (1, 1, "Ada", "Lovelace"),    # Single, one night
    (2, 3, "Grace", "Hopper"),    # Double, three nights
    (3, 5, "Linus", "Torvalds"),  # Suite, five nights
])
def test_create_booking(api_client, roomid, nights, first, last):
    checkin, checkout = future_dates(nights)
    r = api_client.create_booking(BookingClient.payload(roomid, checkin, checkout, first, last))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["roomid"] == roomid
    assert body["firstname"] == first and body["lastname"] == last
    assert body["bookingdates"] == {"checkin": checkin, "checkout": checkout}
    api_client.delete_booking(body["bookingid"])


def test_get_booking(api_client, booking):
    r = api_client.get_booking(booking["bookingid"])
    assert r.status_code == 200
    assert r.json()["lastname"] == booking["lastname"]
    assert r.json()["bookingdates"] == booking["bookingdates"]


def test_update_booking(api_client, booking):
    checkin, checkout = future_dates()  # dates must change or the API 409s on itself
    updated = {**booking, "lastname": "Updated",
               "bookingdates": {"checkin": checkin, "checkout": checkout}}
    r = api_client.update_booking(booking["bookingid"], updated)
    assert r.status_code == 200, r.text
    assert api_client.get_booking(booking["bookingid"]).json()["lastname"] == "Updated"


def test_delete_booking(api_client):
    checkin, checkout = future_dates()
    bid = api_client.create_booking(BookingClient.payload(2, checkin, checkout)).json()["bookingid"]
    assert api_client.delete_booking(bid).status_code == 202
    assert api_client.get_booking(bid).status_code == 404


@pytest.mark.parametrize("bad, expected_error", [
    ({"firstname": ""}, "Firstname should not be blank"),
    ({"lastname": ""}, "Lastname should not be blank"),
    ({"phone": "123"}, "size must be between 11 and 21"),
])
def test_create_booking_invalid_payload(api_client, bad, expected_error):
    checkin, checkout = future_dates()
    r = api_client.create_booking({**BookingClient.payload(1, checkin, checkout), **bad})
    assert r.status_code == 400
    assert expected_error in r.json()["errors"]


def test_get_unknown_booking(api_client):
    assert api_client.get_booking(999999).status_code == 404
