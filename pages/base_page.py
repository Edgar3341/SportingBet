from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:

    def __init__(self, driver, url):
        # Constructor to initialize the browser driver and URL
        self.driver = driver
        self.url = url

    def open(self):
        # Open the URL in the browser
        self.driver.get(self.url)

    # Wait until an element is visible and return it
    def element_is_visible(self, locator, timeout=5):
        return wait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    # Wait until multiple elements are visible and return them
    def elements_are_visible(self, locator, timeout=5):
        return wait(self.driver, timeout).until(EC.visibility_of_all_elements_located(locator))

    # Wait until an element is present in the DOM
    def element_is_present(self, locator, timeout=5):
        return wait(self.driver, timeout).until(EC.presence_of_element_located(locator))

    # Wait until multiple elements are present in the DOM
    def elements_are_present(self, locator, timeout=10):
        return wait(self.driver, timeout).until(EC.presence_of_all_elements_located(locator))

    # Wait until an element is no longer visible
    def element_is_not_visible(self, locator, timeout=5):
        return wait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))

    # Wait until an element is clickable and return it
    def element_is_clickable(self, locator, timeout=5):
        return wait(self.driver, timeout).until(EC.element_to_be_clickable(locator))

    # Scroll the browser to a specific element
    def go_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)


    