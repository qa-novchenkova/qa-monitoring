# Описание страницы входа saucedemo: где что лежит и что можно делать. (скелет страницы, если id 
#поменяется нужно будет поправить только здесь, а не во всех тестахещ)

from selenium.webdriver.common.by import By


class LoginPage:
    URL = "https://www.saucedemo.com/"

    # Локаторы — "адреса" элементов на странице:
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")  # блок с текстом ошибки

    def __init__(self, driver):
        self.driver = driver

    def open(self):
        self.driver.get(self.URL)

    def login(self, username, password):
        self.driver.find_element(*self.USERNAME).send_keys(username)
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.LOGIN_BUTTON).click()

    def get_error(self):
        return self.driver.find_element(*self.ERROR).text