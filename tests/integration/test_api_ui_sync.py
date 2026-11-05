"""Cross-layer checks: what one layer writes, the other must see."""
import time
from datetime import date

import pytest

from conftest import future_dates
from pages.admin_page import AdminPage
from pages.booking_page import BookingPage

pytestmark = pytest.mark.integration

ROOM_NAMES = {1: "101", 2: "102", 3: "103"}


def month_label(iso):
    return date.fromisoformat(iso).strftime("%B %Y")


def eventually(fn, ok=bool, timeout=20, interval=2):
    """Poll fn() until ok(result); return the last result either way. Absorbs demo-site lag/resets."""
    end = time.time() + timeout
    while True:
        result = fn()
        if ok(result) or time.time() >= end:
            return result
        time.sleep(interval)


def report_events_for(driver, checkin):
    admin = AdminPage(driver).login().open_report()
    return admin.go_to_month(month_label(checkin)).event_titles()


def test_api_created_booking_appears_in_admin_report(driver, booking):
    expected = f"{booking['firstname']} {booking['lastname']} - Room: {ROOM_NAMES[booking['roomid']]}"
    checkin = booking["bookingdates"]["checkin"]
    assert expected in eventually(lambda: report_events_for(driver, checkin), lambda e: expected in e)


def test_api_deleted_booking_disappears_from_admin_report(driver, api_client, booking):
    checkin = booking["bookingdates"]["checkin"]
    expected = f"{booking['firstname']} {booking['lastname']} - Room: {ROOM_NAMES[booking['roomid']]}"
    assert expected in eventually(lambda: report_events_for(driver, checkin), lambda e: expected in e)

    assert api_client.delete_booking(booking["bookingid"]).status_code == 202
    assert expected not in eventually(lambda: report_events_for(driver, checkin), lambda e: expected not in e)


def test_ui_created_booking_is_readable_via_api(driver, api_client):
    checkin, checkout = future_dates(2)
    page = BookingPage(driver).open_room(2, checkin, checkout).book("Browser", "Made")
    assert page.confirmation_title() == "Booking Confirmed"  # wait for the POST to land
    matches = eventually(lambda: [b for b in api_client.list_bookings(2)
                                  if b["bookingdates"] == {"checkin": checkin, "checkout": checkout}])
    assert len(matches) == 1, matches
    assert matches[0]["firstname"] == "Browser" and matches[0]["lastname"] == "Made"
    assert api_client.delete_booking(matches[0]["bookingid"]).status_code == 202
    assert api_client.get_booking(matches[0]["bookingid"]).status_code == 404
