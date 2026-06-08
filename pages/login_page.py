# Page Object страницы входа saucedemo.
# Идея паттерна: всё про страницу (адреса элементов + действия) держим в одном классе.
# Если на сайте поменяется id поля — правим только здесь, а не в каждом тесте. В тестах потом импортируем эту структуру

from selenium.webdriver.common.by import By  # способы поиска элементов (по id, css и т.д.)


class LoginPage:
    URL = "https://www.saucedemo.com/"        # адрес страницы входа

    # Локаторы — "адреса" элементов (пара: способ поиска + значение).
    USERNAME = (By.ID, "user-name")           # поле логина
    PASSWORD = (By.ID, "password")            # поле пароля
    LOGIN_BUTTON = (By.ID, "login-button")    # кнопка Login
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")  # блок с текстом ошибки

    def __init__(self, driver):
        self.driver = driver                  # браузер из фикстуры — через него работаем со страницей

    def open(self):
        """Открыть страницу входа."""
        self.driver.get(self.URL)

    def login(self, username, password):
        """Ввести логин/пароль и нажать кнопку входа."""
        # *self.USERNAME распаковывает пару (By.ID, "user-name") в два аргумента find_element
        self.driver.find_element(*self.USERNAME).send_keys(username)
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.LOGIN_BUTTON).click()

    def get_error(self):
        """Вернуть текст сообщения об ошибке входа."""
        return self.driver.find_element(*self.ERROR).text