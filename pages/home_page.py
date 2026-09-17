from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    path = "/"
    ROOM_CARDS = (By.CSS_SELECTOR, ".room-card")
    BOOK_NOW_LINKS = (By.CSS_SELECTOR, ".room-card a.btn")

    def room_types(self):
        self.find(self.ROOM_CARDS)
        return [c.find_element(By.CSS_SELECTOR, ".card-title, h5, h3").text
                for c in self.driver.find_elements(*self.ROOM_CARDS)]

    def book_room(self, index):
        """Click the Nth room's 'Book now' link; lands on the reservation page."""
        self.find(self.ROOM_CARDS)
        self.click((By.XPATH, f"(//div[contains(@class,'room-card')]//a[contains(@class,'btn')])[{index + 1}]"))
