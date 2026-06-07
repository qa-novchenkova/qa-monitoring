# Проверяем, что пользователь может залогиниться на saucedemo.
# Тесты входа. Браузер берём из фикстуры driver (см. conftest.py).
# Каждый тест принимает аргумент driver — это фикстура из conftest.py
# (pytest сам подставит готовый браузер).

from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


def test_login_success(driver):
    """Успешный вход: верные логин/пароль -> попадаем на страницу товаров."""
    login = LoginPage(driver)                       # объект страницы входа
    login.open()                                    # открываем сайт
    login.login("standard_user", "secret_sauce")    # вводим верные данные

    inventory = InventoryPage(driver)               # объект страницы товаров
    assert inventory.is_opened()                    # проверка: открылась страница Products


def test_login_wrong_password(driver):
    """Неуспешный вход: неверный пароль -> показывается ошибка."""
    login = LoginPage(driver)
    login.open()
    login.login("standard_user", "wrong_password")  # намеренно неверный пароль

    # saucedemo при неверных данных выводит ошибку с текстом "...do not match..."
    assert "do not match" in login.get_error()