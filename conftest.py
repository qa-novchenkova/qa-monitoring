# conftest.py — общий файл pytest с "фикстурами" (заготовками для тестов).
# pytest сам находит этот файл и подставляет фикстуру в тест, которому она нужна
# (тест просто принимает аргумент с именем фикстуры, например driver).
#
# Здесь живёт фикстура driver: открывает браузер ДО теста и закрывает ПОСЛЕ,
# чтобы не дублировать этот код в каждом тесте.

import os                                               # чтение переменных окружения (для HEADLESS)
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options   # настройки запуска Chrome


@pytest.fixture                                         # помечаем функцию как фикстуру pytest
def driver():
    # Настройки браузера
    options = Options()
    options.add_argument("--log-level=3")               # показывать только серьёзные сообщения Chrome
    options.add_experimental_option("excludeSwitches", ["enable-logging"])  # убрать "шум" в консоли

    # На сервере GitHub (CI) нет экрана -> браузер запускаем без окна (headless).
    # Локально переменной HEADLESS нет -> браузер открывается видимым окном.
    if os.getenv("HEADLESS") == "true":
        options.add_argument("--headless=new")          # режим без видимого окна
        options.add_argument("--window-size=1920,1080") # размер "экрана" для headless

    # --- ПОДГОТОВКА: выполняется ДО каждого теста ---
    driver = webdriver.Chrome(options=options)          # запускаем браузер с настройками
    driver.implicitly_wait(10)                           # ждать элемент до 10 сек, прежде чем упасть
    driver.maximize_window()                            # развернуть окно

    yield driver                                        # отдаём браузер в тест и "замираем" здесь

    # --- УБОРКА: выполняется ПОСЛЕ каждого теста (даже если он упал) ---
    driver.quit()                                       # закрываем браузер, чтобы не висел в памяти