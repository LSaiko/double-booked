from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class BookingPage(BasePage):
    """Reservation page: /reservation/<roomid>?checkin=YYYY-MM-DD&checkout=YYYY-MM-DD"""
    TITLE = (By.CSS_SELECTOR, "h1")
    RESERVE_NOW = (By.XPATH, "//button[normalize-space()='Reserve Now']")
    FIRSTNAME = (By.NAME, "firstname")
    LASTNAME = (By.NAME, "lastname")
    EMAIL = (By.NAME, "email")
    PHONE = (By.NAME, "phone")
    TOTAL = (By.XPATH, "//div[contains(@class,'card')]//span[contains(text(),'Total')]/following-sibling::span")
    CONFIRMATION_TITLE = (By.XPATH, "//h2[normalize-space()='Booking Confirmed']")
    CONFIRMATION_DATES = (By.XPATH, "//h2[normalize-space()='Booking Confirmed']/following::strong[1]")
    ERRORS = (By.CSS_SELECTOR, ".alert-danger, .alert-danger li")

    def open_room(self, roomid, checkin, checkout):
        return self.open(f"/reservation/{roomid}?checkin={checkin}&checkout={checkout}")

    def room_title(self):
        return self.find(self.TITLE).text

    def start_reservation(self):
        self.click(self.RESERVE_NOW)
        self.find(self.FIRSTNAME)
        return self

    def fill_guest_details(self, firstname, lastname, email, phone):
        self.type(self.FIRSTNAME, firstname)
        self.type(self.LASTNAME, lastname)
        self.type(self.EMAIL, email)
        self.type(self.PHONE, phone)
        return self

    def submit(self):
        self.click(self.RESERVE_NOW)
        return self

    def book(self, firstname, lastname, email="guest@example.com", phone="01234567890"):
        return self.start_reservation().fill_guest_details(firstname, lastname, email, phone).submit()

    def confirmation_title(self):
        return self.find(self.CONFIRMATION_TITLE).text

    def confirmed_dates(self):
        return self.find(self.CONFIRMATION_DATES).text

    def error_messages(self):
        self.find(self.ERRORS)
        return [e.text for e in self.driver.find_elements(*self.ERRORS) if e.text.strip()]
