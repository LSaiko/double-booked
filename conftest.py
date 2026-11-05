import functools
import random
from datetime import date, timedelta
from pathlib import Path

import pytest
import requests
from selenium import webdriver

from api.booking_client import BookingClient
from config import API_URL, HEADLESS


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # expose the test outcome to fixtures so `driver` can screenshot on failure
    outcome = yield
    item.rep_call = outcome.get_result() if call.when == "call" else getattr(item, "rep_call", None)


@pytest.fixture
def driver(request):
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,1000")
    d = webdriver.Chrome(options=opts)
    d.implicitly_wait(5)
    yield d
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        Path("screenshots").mkdir(exist_ok=True)
        d.save_screenshot(f"screenshots/{request.node.name}.png")
    d.quit()


@pytest.fixture(scope="session")
def api_client():
    return BookingClient()


# Upstream outage since 2026-10-14: these endpoints answer 500 to everything,
# including to anonymous callers who would normally get a 403. /booking/{id}
# takes out the API CRUD and security tests; /room/{id} leaves the reservation
# page stuck on its spinner, so every UI locator on it times out.
# ponytail: one probe per path per session, and marked tests skip themselves
# while it is down. Both the markers and this go once upstream stays up.
BROKEN_UPSTREAM = {"booking_by_id": "/booking/1", "room_by_id": "/room/1"}


@functools.cache
def endpoint_up(path):
    return requests.get(f"{API_URL}{path}").status_code != 500


@pytest.fixture(autouse=True)
def _skip_if_upstream_down(request):
    for marker, path in BROKEN_UPSTREAM.items():
        if request.node.get_closest_marker(marker) and not endpoint_up(path):
            pytest.skip(f"upstream: {path.rsplit('/', 1)[0]}/{{id}} returns 500")


def future_dates(nights=2):
    """Random check-in 60..700 days out, as ISO strings.

    ponytail: random dates avoid 409 clashes with leftover bookings on the shared
    demo site; swap for a real free-slot lookup if collisions ever show up.
    """
    checkin = date.today() + timedelta(days=random.randint(60, 700))
    return checkin.isoformat(), (checkin + timedelta(days=nights)).isoformat()


@pytest.fixture
def booking(api_client):
    """Create a booking via the API, delete it after the test."""
    checkin, checkout = future_dates()
    data = BookingClient.payload(roomid=1, checkin=checkin, checkout=checkout,
                                 firstname="Api", lastname=f"Made{random.randint(100, 999)}")
    r = api_client.create_booking(data)
    assert r.status_code == 201, r.text
    data["bookingid"] = r.json()["bookingid"]
    yield data
    api_client.delete_booking(data["bookingid"])
