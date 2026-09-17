from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import BASE_URL


class BasePage:
    path = "/"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self, path=None):
        url = BASE_URL + (path if path is not None else self.path)
        # ponytail: one retry for Chrome's transient "This page couldn't load"
        # error page; bump to a loop with backoff if it keeps showing up in CI
        for _ in range(2):
            self.driver.get(url)
            if "page couldn" not in self.driver.find_element(By.TAG_NAME, "body").text:
                break
        return self

    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator):
        # scrollIntoView + JS click: the sticky navbar intercepts native clicks
        el = self.wait.until(EC.presence_of_element_located(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", el)

    def type(self, locator, text):
        el = self.find(locator)
        el.clear()
        el.send_keys(text)
