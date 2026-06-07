# Проверяем, что пользователь может залогиниться на saucedemo.
# Тесты входа. Браузер берём из фикстуры driver (см. conftest.py).

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


def test_login_success(driver):
    login = LoginPage(driver)
    login.open()
    login.login("standard_user", "secret_sauce")

    inventory = InventoryPage(driver)
    assert inventory.is_opened()   # ожидаем страницу Products


def test_login_wrong_password(driver):
    login = LoginPage(driver)
    login.open()
    login.login("standard_user", "wrong_password")

    # при неверных данных saucedemo показывает ошибку с текстом "do not match"
    assert "do not match" in login.get_error()