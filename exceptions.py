class Error(Exception):
    """Базовый класс ошибок."""
    pass


class SendMessageError(Error):
    """Не удалось отправить сообщение."""
    pass


class UnexpectedStatusCodeError(Error):
    """Ответ API содержит статус код, отличный от 200."""
    pass


class ExpectedKeysNotFoundError(Error):
    """Отсутствие ожидаемых ключей в ответе API."""
    pass


class UnexpectedStatusError(Error):
    """Обнаружен недокументированный статус домашней работы в ответе API."""
    pass
