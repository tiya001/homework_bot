import os
import time
from http import HTTPStatus
import requests
import logging
from logging.handlers import RotatingFileHandler
import telegram

from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5,
)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(
            f'Отправлено сообщение {message} пользователю: {TELEGRAM_CHAT_ID}'
        )
    except Exception as Error:
        logger.error(
            f'Сообщение {message} не отправлено'
            f'Причина: {Error}'
        )

def get_api_answer(current_timestamp):
    try:
        timestamp = current_timestamp or int(time.time())
        params = {'from_date': timestamp}
        homework_status = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
        if homework_status.status_code != HTTPStatus.OK:
            logger.error(f'Ошибка при запросе к API')
            raise Exception('Ошибка при запросе к API')
        homework_status_py = homework_status.json()
        return homework_status_py
    except Exception as Error:
        logger.error(f'Ошибка {Error} при запросе к API')
        raise Exception(f'Ошибка{Error}')


def check_response(response):
    homework_list = response['homeworks']
    if not isinstance(homework_list, list):
        logger.error(f'Тип данных: {type(homework_list)}, ожидался: list')
        raise TypeError()
    if not homework_list:
        logger.error('Список с домашками пуст')
    else:
        homework = homework_list[0]
        return homework


def parse_status(homework):
    if not isinstance(homework, dict):
        logger.error('Ошибка типа данных в homework')
        raise KeyError('Missing "homework_name" key in API response')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except Exception as Error:
        logger.error('Список домашних работ пуст')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return False
    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_message = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            check = check_response(response)
            message = parse_status(check)
            if last_message != message:
                last_message = message
                send_message(bot, last_message)
                time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()