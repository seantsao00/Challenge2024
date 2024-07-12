from typing import Callable

from instances_manager import get_model


class LinearAnimationEasings:
    """easing functions from https://easings.net/"""

    @staticmethod
    def linear(t: float):
        return t

    @staticmethod
    def easeInOutCubic(t: float):
        if t < 0.5:
            return 4 * (t ** 3)
        return 1 - ((-2 * t + 2) ** 3) / 2

    @staticmethod
    def easeOutCubic(t: float):
        return 1 - (1 - t) ** 3


class LinearAnimation:
    def __init__(self, initial_value: float, duration: float, easing: Callable[[float], float] = LinearAnimationEasings.easeInOutCubic):
        # immutable
        self.__duration = duration
        self.__easing = easing
        # mutable
        self.__initial_value = initial_value
        self.__target_value = initial_value
        self.__end_time = -1e9

    @property
    def value(self):
        cur_time = get_model().get_time()
        if cur_time >= self.__end_time:
            return self.__target_value
        # animate with linear interpolation
        incompleteness = 1 - (self.__end_time - cur_time) / self.__duration
        ratio = self.__easing(incompleteness)
        return self.__initial_value * (1 - ratio) + self.__target_value * ratio

    @value.setter
    def value(self, target_value):
        if target_value == self.__target_value:
            return
        self.__initial_value = self.value
        self.__target_value = target_value
        self.__end_time = get_model().get_time() + self.__duration
