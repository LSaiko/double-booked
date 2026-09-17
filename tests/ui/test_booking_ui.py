import pytest

from conftest import future_dates
from pages.booking_page import BookingPage
from pages.home_page import HomePage

pytestmark = pytest.mark.ui


def test_home_lists_rooms_and_navigates_to_booking(driver):
    home = HomePage(driver).open()
    assert home.room_types() == ["Single", "Double", "Suite"]
    home.book_room(0)
    assert "/reservation/1" in driver.current_url
    assert BookingPage(driver).room_title() == "Single Room"


@pytest.mark.parametrize("roomid, nights, title", [
    (1, 2, "Single Room"),
    (2, 3, "Double Room"),
    (3, 1, "Suite Room"),
])
def test_booking_form_to_confirmation(driver, api_client, roomid, nights, title):
    checkin, checkout = future_dates(nights)
    page = BookingPage(driver).open_room(roomid, checkin, checkout)
    assert page.room_title() == title
    page.book("Selenium", "Tester")
    assert page.confirmation_title() == "Booking Confirmed"
    assert page.confirmed_dates() == f"{checkin} - {checkout}"
    # cleanup: find it through the API so the next run has a clean room
    for b in api_client.get_bookings(roomid).json()["bookings"]:
        if b["bookingdates"]["checkin"] == checkin and b["lastname"] == "Tester":
            api_client.delete_booking(b["bookingid"])


def test_booking_form_rejects_blank_names(driver):
    checkin, checkout = future_dates()
    page = BookingPage(driver).open_room(1, checkin, checkout)
    page.start_reservation().fill_guest_details("", "", "x@example.com", "01234567890").submit()
    errors = " ".join(page.error_messages())
    assert "Firstname should not be blank" in errors
    assert "Lastname should not be blank" in errors
