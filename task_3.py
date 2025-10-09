import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# --- КОНФИГУРАЦИЯ ---
DAYS_TO_FETCH = 90
CBR_API_URL = "http://www.cbr.ru/scripts/XML_daily.asp" # Используем русскую версию, eng-версия может быть недоступна

def get_cbr_rates():
    """
    Основная функция для получения и анализа данных от ЦБ РФ.
    """
    print(f"Запускаю анализ курсов валют за последние {DAYS_TO_FETCH} дней...")

    # Инициализация переменных для хранения экстремумов и среднего
    max_rate_info = {'value': 0.0, 'name': '', 'date': ''}
    min_rate_info = {'value': float('inf'), 'name': '', 'date': ''}
    all_rates_sum = 0.0
    all_rates_count = 0

    # 1. Генерируем даты и итерируемся по ним в обратном порядке
    today = datetime.now()
    for i in range(DAYS_TO_FETCH):
        current_date = today - timedelta(days=i)
        date_str_for_api = current_date.strftime('%d/%m/%Y')
        
        print(f"Обрабатываю дату: {date_str_for_api}...", end=" ")

        try:
            # 2. Делаем запрос к API
            response = requests.get(CBR_API_URL, params={'date_req': date_str_for_api}, timeout=5)
            response.raise_for_status() # Бросит исключение для плохих ответов (4xx, 5xx)

            # 3. Парсим XML
            root = ET.fromstring(response.content)
            
            # Проверяем, есть ли вообще данные на эту дату
            if not root.findall('Valute'):
                print("Нет данных (выходной/праздник).")
                continue

            for currency in root.findall('Valute'):
                name = currency.find('Name').text
                # ВАЖНО: Приводим значение к реальному курсу за 1 единицу
                nominal = int(currency.find('Nominal').text)
                value_str = currency.find('Value').text.replace(',', '.')
                value = float(value_str)
                
                actual_rate = value / nominal

                # Обновляем агрегированные данные
                all_rates_sum += actual_rate
                all_rates_count += 1

                # Проверяем на максимум
                if actual_rate > max_rate_info['value']:
                    max_rate_info['value'] = actual_rate
                    max_rate_info['name'] = name
                    max_rate_info['date'] = date_str_for_api
                
                # Проверяем на минимум
                if actual_rate < min_rate_info['value']:
                    min_rate_info['value'] = actual_rate
                    min_rate_info['name'] = name
                    min_rate_info['date'] = date_str_for_api
            
            print("OK")

        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
        except ET.ParseError as e:
            print(f"Ошибка парсинга XML: {e}")
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")

    # 4. Расчет среднего и вывод результатов
    average_rate = all_rates_sum / all_rates_count if all_rates_count > 0 else 0

    print("\n" + "="*40)
    print("АНАЛИЗ ЗАВЕРШЕН. РЕЗУЛЬТАТЫ:")
    print("="*40)
    
    print("\n[МАКСИМАЛЬНЫЙ КУРС]")
    print(f"  Валюта:     {max_rate_info['name']}")
    print(f"  Значение:   {max_rate_info['value']:.4f} RUB")
    print(f"  Дата:       {max_rate_info['date']}")

    print("\n[МИНИМАЛЬНЫЙ КУРС]")
    print(f"  Валюта:     {min_rate_info['name']}")
    print(f"  Значение:   {min_rate_info['value']:.4f} RUB")
    print(f"  Дата:       {min_rate_info['date']}")

    print("\n[СРЕДНЕЕ ЗНАЧЕНИЕ]")
    print(f"  Средний курс по всем валютам за период: {average_rate:.4f} RUB")
    print("="*40)


if __name__ == "__main__":
    # Установка правильной кодировки для Windows, если скрипт запускается из cmd
    import sys
    import os
    if os.name == 'nt':
        sys.stdout.reconfigure(encoding='utf-8')
        
    get_cbr_rates()