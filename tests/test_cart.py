# Тест корзины: после входа добавляем товар и проверяем счётчик на иконке корзины.

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


def test_add_to_cart(driver):
    """Добавление товара в корзину увеличивает счётчик до 1."""
    login = LoginPage(driver)
    login.open()
    login.login("standard_user", "secret_sauce")    # сначала входим

    inventory = InventoryPage(driver)
    inventory.add_backpack_to_cart()                 # добавляем рюкзак

    assert inventory.get_cart_count() == "1"         # на иконке корзины должна быть "1"