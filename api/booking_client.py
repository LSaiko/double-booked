import requests

from config import ADMIN_PASS, ADMIN_USER, API_URL


class BookingClient:
    """Thin wrapper over the restful-booker-platform booking API.

    Every method returns the raw `requests.Response` so tests assert on
    status codes and bodies directly.
    """

    def __init__(self, base_url=API_URL, auth=True):
        self.base_url = base_url
        self.session = requests.Session()
        if auth:
            self.login()

    def login(self, username=ADMIN_USER, password=ADMIN_PASS):
        r = self.session.post(f"{self.base_url}/auth/login",
                              json={"username": username, "password": password})
        r.raise_for_status()
        self.set_token(r.json()["token"])
        return r

    def set_token(self, token):
        # GET/PUT/DELETE on bookings require the token as a cookie
        self.session.cookies.set("token", token)

    @staticmethod
    def payload(roomid=1, checkin="2027-05-01", checkout="2027-05-03", firstname="Test",
                lastname="User", email="test.user@example.com", phone="01234567890",
                depositpaid=True):
        return {
            "roomid": roomid, "firstname": firstname, "lastname": lastname,
            "depositpaid": depositpaid, "email": email, "phone": phone,
            "bookingdates": {"checkin": checkin, "checkout": checkout},
        }

    def create_booking(self, data):
        return self.session.post(f"{self.base_url}/booking", json=data)

    def get_booking(self, booking_id):
        return self.session.get(f"{self.base_url}/booking/{booking_id}")

    def get_bookings(self, roomid):
        return self.session.get(f"{self.base_url}/booking", params={"roomid": roomid})

    def list_bookings(self, roomid):
        """Bookings for a room as a list. The demo site has returned both
        {"bookings": [...]} and a bare [...] for this endpoint, so normalise."""
        body = self.get_bookings(roomid).json()
        return body["bookings"] if isinstance(body, dict) else body

    def update_booking(self, booking_id, data):
        # NB: site returns 409 if the dates are unchanged (it conflicts with itself)
        return self.session.put(f"{self.base_url}/booking/{booking_id}", json=data)

    def delete_booking(self, booking_id):
        return self.session.delete(f"{self.base_url}/booking/{booking_id}")
