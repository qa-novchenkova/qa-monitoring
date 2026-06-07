# conftest.py — общие "заготовки" (фикстуры) для всех тестов.
# pytest сам находит этот файл и применяет фикстуры там, где они нужны.
# фикстура driver один раз открывает и закрывает браузер для всех тестов.


import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def driver():
    # Настройки браузера: глушим лишние технические сообщения в консоли
    options = Options()
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # В CI (на сервере GitHub) нет экрана — запускаем браузер без окна.
    if os.getenv("HEADLESS") == "true":
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    # --- ПОДГОТОВКА (до теста) ---
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.maximize_window()

    yield driver # отдаём готовый браузер в тест

    # --- УБОРКА (после теста, всегда) ---
    driver.quit()