from selenium.webdriver.common.by import By

from config import ADMIN_PASS, ADMIN_USER
from pages.base_page import BasePage


class AdminPage(BasePage):
    """Admin login + the Report calendar, where every booking shows as an event."""
    path = "/admin"
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    LOGIN = (By.ID, "doLogin")
    ROOMS_NAV = (By.LINK_TEXT, "Rooms")
    MONTH_LABEL = (By.CSS_SELECTOR, ".rbc-toolbar-label")
    NEXT_MONTH = (By.XPATH, "//button[normalize-space()='Next']")
    EVENTS = (By.CSS_SELECTOR, ".rbc-event-content")

    def login(self, username=ADMIN_USER, password=ADMIN_PASS):
        self.open()
        if self.driver.find_elements(*self.ROOMS_NAV):  # already logged in this session
            return self
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN)
        self.find(self.ROOMS_NAV)
        return self

    def open_report(self):
        self.open("/admin/report")
        self.find(self.MONTH_LABEL)
        return self

    def go_to_month(self, label, max_clicks=36):
        """Click Next until the calendar shows e.g. 'May 2027'."""
        for _ in range(max_clicks):
            if self.find(self.MONTH_LABEL).text == label:
                return self
            self.click(self.NEXT_MONTH)
        raise AssertionError(f"month {label!r} not reached in {max_clicks} clicks")

    def event_titles(self):
        return [e.text for e in self.driver.find_elements(*self.EVENTS)]
