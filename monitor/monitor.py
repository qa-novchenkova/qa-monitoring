# Монитор доступности сайтов.
# Что делает:
#   1) читает список сайтов из targets.yaml;
#   2) по каждому делает HTTP-запрос, замеряет код ответа и время ответа;
#   3) пишет результат в консоль и в файл logs/monitor.log (структурированный JSON);
#   4) (если включено) отправляет результат в Elasticsearch — для графиков в Kibana;
#   5) если хоть один сайт недоступен — завершается с кодом 1
#      (в CI это делает прогон красным = срабатывает как алерт).
#
# Запуск локально:  python monitor/monitor.py

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml
from elasticsearch import Elasticsearch

# --- Настройки ---
CONFIG_PATH = Path(__file__).parent / "targets.yaml"               # файл со списком сайтов
LOG_PATH = Path(__file__).parent.parent / "logs" / "monitor.log"   # куда писать лог
TIMEOUT = 10                                                       # ждём ответ не дольше 10 сек

# Адрес ES и флаг отправки берём из переменных окружения.
# Локально по умолчанию шлём в localhost; в CI отправку выключаем (там ES недоступен).
ES_HOST = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ENABLE_ES = os.getenv("ENABLE_ES", "true").lower() == "true"
ES_INDEX = "site-monitoring"                                       # "папка" в Elasticsearch


def load_targets():
    """Читаем список сайтов из YAML-конфига."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)["targets"]


def check(target):
    """Проверяем один сайт и возвращаем результат словарём."""
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),  # время проверки (UTC)
        "target_name": target["name"],
        "url": target["url"],
    }
    try:
        response = requests.get(target["url"], timeout=TIMEOUT)
        result["status_code"] = response.status_code
        result["response_time_ms"] = round(response.elapsed.total_seconds() * 1000)
        # UP, если код ответа меньше 400 (нет ошибок клиента/сервера)
        result["status"] = "UP" if response.status_code < 400 else "DOWN"
    except requests.RequestException as e:
        # Сайт вообще не ответил (таймаут, нет связи и т.п.)
        result["status_code"] = None
        result["response_time_ms"] = None
        result["status"] = "DOWN"
        result["error"] = str(e)
    return result


def save_log(result):
    """Печатаем результат и дописываем строкой в лог-файл."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)   # создаём папку logs, если её нет
    line = json.dumps(result, ensure_ascii=False)        # словарь -> строка JSON
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")                             # каждая проверка — отдельной строкой


def send_to_elasticsearch(result):
    """Отправляем проверку в Elasticsearch. При ошибке не падаем, а предупреждаем."""
    try:
        es = Elasticsearch(ES_HOST)
        es.index(index=ES_INDEX, document=result)
    except Exception as e:
        print(f"[!] Не удалось отправить в Elasticsearch: {e}")


def main():
    any_down = False                       # встретился ли хоть один недоступный сайт
    for target in load_targets():
        result = check(target)
        save_log(result)
        if ENABLE_ES:                      # в CI отправку в ES отключаем флагом
            send_to_elasticsearch(result)
        if result["status"] == "DOWN":
            any_down = True

    # Если что-то недоступно — выходим с ошибкой, чтобы прогон в CI стал красным (алерт).
    if any_down:
        sys.exit(1)


if __name__ == "__main__":
    main()