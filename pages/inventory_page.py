# Описание страницы с товарами (Products), куда попадаем после успешного входа.
# *self.USERNAME — звёздочка «распаковывает» пару (By.ID, "user-name") в два аргумента для find_element

from selenium.webdriver.common.by import By


class InventoryPage:
    TITLE = (By.CLASS_NAME, "title")                       # заголовок "Products"
    ADD_BACKPACK = (By.ID, "add-to-cart-sauce-labs-backpack")  # кнопка "добавить рюкзак"
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")    # счётчик товаров на иконке корзины

    def __init__(self, driver):
        self.driver = driver

    def is_opened(self):
        return self.driver.find_element(*self.TITLE).text == "Products"

    def add_backpack_to_cart(self):
        self.driver.find_element(*self.ADD_BACKPACK).click()

    def get_cart_count(self):
        return self.driver.find_element(*self.CART_BADGE).text