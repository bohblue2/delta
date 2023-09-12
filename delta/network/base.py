import abc
from typing import Any


class BaseNetworkPublisher(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def publish(self, topic: str, msg: Any) -> None:
        ...
