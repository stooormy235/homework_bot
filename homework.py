import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
import telegram


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler(sys.stdout)])
logger = logging.getLogger('bot_logger')

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка токенов."""
    tokens = [
        'PRACTICUM_TOKEN',
        'TELEGRAM_TOKEN',
        'TELEGRAM_CHAT_ID',
    ]
    if not PRACTICUM_TOKEN:
        logger.critical('Отсутствует токен: "PRACTICUM_TOKEN"')
        return False
    if not TELEGRAM_TOKEN:
        logger.critical('Отсутствует токен: "TELEGRAM_TOKEN"')
        return False
    if not TELEGRAM_CHAT_ID:
        logger.critical('Отсутствует телеграм: "TELEGRAM_CHAT_ID"')
        return False
    for token in tokens:
        if (token) is None:
            logger.critical(f'Отсутствует переменная: {token}')
            raise Exception(f'Отсутствует переменная: {token}')
    return True


def send_message(bot, message):
    """Отправка сообщения в телеграмм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Сообщение отправлено: {message}')
    except Exception as error:
        logging.error(f'Error while getting list of homeworks: {error}')


def get_api_answer(timestamp):
    """Запрос к API-Сервиса."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload,
        )
        status = homework_statuses.status_code
        if status == HTTPStatus.OK:
            return homework_statuses.json()
        else:
            logging.error('Ошибка запроса')
            send_message(bot, 'Ошибка запроса')
            raise ValueError(homework_statuses.json())
    except Exception:
        logging.error('Сбой в работе эндпоинта')
        raise ValueError('Сбой в работе эндпоинта')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if isinstance(response, dict) is False:
        logging.error('Данные получены не в виде словаря')
        raise TypeError
    if 'homeworks' not in response:
        logging.error('Нет ключа homeworks')
        raise KeyError
    if isinstance(response['homeworks'], list) is False:
        logging.error('Данные переданы не в виде списка')
        raise TypeError
    if 'current_date'not in response:
        logging.error('Отсутствует ожидаемый ключ current_date в ответе API')
        raise KeyError
    if type(response) is None:
        logging.error('Данные получены с типом None')
        raise TypeError


def parse_status(homework):
    """Получает статус домашней работы."""
    try:
        homework_name = str(homework['homework_name'])
    except Exception:
        logging.error('Не удалось узнать название работы')
    try:
        homework_status = homework['status']
    except Exception:
        logging.error('Не удалось узнать статус работы')
    if homework_status == 'approved':
        verdict = str(HOMEWORK_VERDICTS[homework_status])
        return str(
            f'Изменился статус проверки работы "{homework_name}". {verdict}'
        )
    elif homework_status == 'reviewing':
        verdict = str(HOMEWORK_VERDICTS[homework_status])
        return str(
            f'Изменился статус проверки работы "{homework_name}". {verdict}'
        )
    elif homework_status == 'rejected':
        verdict = str(HOMEWORK_VERDICTS[homework_status])
        return str(
            f'Изменился статус проверки работы "{homework_name}". {verdict}'
        )
    else:
        logging.error('Не обнаружен статус домашней робаты')
        raise KeyError


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        format='%(asctime)s, %(levelname)s, %(message)s',
        handlers=[logging.FileHandler('log.txt')]
    )
    if check_tokens():
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        timestamp = int(time.time() - 1814400)
        first_status = ''
        while True:
            try:
                response = get_api_answer(timestamp)
                check_response(response)
                new_status = parse_status(response['homeworks'][0])
                if new_status != first_status:
                    send_message(bot, new_status)
                first_status = new_status
            except Exception as error:
                message = f'Сбой в работе программы: {error}'
                logging.error(message)
                send_message(bot, message)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
