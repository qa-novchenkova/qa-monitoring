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


def send_telegram(message):
    """Отправляем сообщение в Telegram. Токен и chat_id берём из переменных окружения.
    Если они не заданы — тихо пропускаем (значит, уведомления не настроены)."""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": message},
            timeout=10,
        )
    except requests.RequestException as e:
        print(f"[!] Не удалось отправить в Telegram: {e}")



def main():
    down_sites = []                        # сюда складываем недоступные сайты
    for target in load_targets():
        result = check(target)
        save_log(result)
        if ENABLE_ES:                      # в CI отправку в ES отключаем флагом
            send_to_elasticsearch(result)
        if result["status"] == "DOWN":
            down_sites.append(result)

    # Если есть падения — формируем текст и шлём уведомление в Telegram
    if down_sites:
        lines = ["⚠️ Обнаружены недоступные сайты:"]
        for r in down_sites:
            reason = r.get("status_code") or r.get("error", "нет ответа")
            lines.append(f"- {r['target_name']} ({r['url']}): {reason}")
        send_telegram("\n".join(lines))

        # выходим с ошибкой, чтобы прогон в CI стал красным (алерт)
        sys.exit(1)


if __name__ == "__main__":
    main()