from abc import ABCMeta, abstractmethod


class APIBase(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self): pass

    @abstractmethod
    def connect_to_api(self, api_key, api_secret): pass
