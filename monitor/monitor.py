# Монитор доступности сайтов.
# 1) проверяет каждый сайт из targets.yaml
# 2) пишет результат в консоль и в файл logs/monitor.log
# 3) отправляет результат в Elasticsearch (для графиков в Kibana)
# Запуск:  python monitor/monitor.py

import json
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml
from elasticsearch import Elasticsearch

CONFIG_PATH = Path(__file__).parent / "targets.yaml"
LOG_PATH = Path(__file__).parent.parent / "logs" / "monitor.log"
TIMEOUT = 10                       # сколько секунд ждём ответа сайта

ES_HOST = "http://localhost:9200"  # адрес Elasticsearch (наш контейнер)
ES_INDEX = "site-monitoring"       # "папка" в Elasticsearch, куда складываем проверки


def load_targets():
    """Читаем список сайтов из YAML-конфига."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)["targets"]


def check(target):
    """Проверяем один сайт и возвращаем результат словарём."""
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_name": target["name"],
        "url": target["url"],
    }
    try:
        response = requests.get(target["url"], timeout=TIMEOUT)
        result["status_code"] = response.status_code
        result["response_time_ms"] = round(response.elapsed.total_seconds() * 1000)
        result["status"] = "UP" if response.status_code < 400 else "DOWN"
    except requests.RequestException as e:
        result["status_code"] = None
        result["response_time_ms"] = None
        result["status"] = "DOWN"
        result["error"] = str(e)
    return result


def save_log(result):
    """Печатаем результат и дописываем строкой в лог-файл."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(result, ensure_ascii=False)
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def send_to_elasticsearch(es, result):
    """Отправляем одну проверку в Elasticsearch. Если ES недоступен — не падаем."""
    try:
        es.index(index=ES_INDEX, document=result)
    except Exception as e:
        print(f"[!] Не удалось отправить в Elasticsearch: {e}")


def main():
    es = Elasticsearch(ES_HOST)
    for target in load_targets():
        result = check(target)
        save_log(result)
        send_to_elasticsearch(es, result)


if __name__ == "__main__":
    main()