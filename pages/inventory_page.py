# Page Object страницы товаров (Products) — сюда попадаем после успешного входа.

from selenium.webdriver.common.by import By


class InventoryPage:
    # Локаторы элементов страницы товаров:
    TITLE = (By.CLASS_NAME, "title")                           # заголовок "Products"
    ADD_BACKPACK = (By.ID, "add-to-cart-sauce-labs-backpack")  # кнопка "добавить рюкзак"
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")        # счётчик товаров на иконке корзины

    def __init__(self, driver):
        self.driver = driver

    def is_opened(self):
        """True, если открыта страница товаров (заголовок == 'Products')."""
        return self.driver.find_element(*self.TITLE).text == "Products"

    def add_backpack_to_cart(self):
        """Нажать 'добавить рюкзак в корзину'."""
        self.driver.find_element(*self.ADD_BACKPACK).click()

    def get_cart_count(self):
        """Вернуть число на иконке корзины как текст (например '1')."""
        return self.driver.find_element(*self.CART_BADGE).text