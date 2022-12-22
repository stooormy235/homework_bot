class UnknownHomeworkStatus(Exception):
    """Неизвестный статус домашнего задания."""

    pass


class KeyHomeworkStatusIsInaccessible(Exception):
    """В ответе API домашки нет ключа homework_name."""

    pass
