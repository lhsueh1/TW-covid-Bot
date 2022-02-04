import logging


class MyException(Exception):

    def __init__(self, *message: str) -> None:
        logging.exception(*message)
        super().__init__(*message)