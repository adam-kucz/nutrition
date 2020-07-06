from abc import abstractmethod
from typing import Mapping, Callable, NamedTuple


# TODO: figure out a standardized way of combining two NamedTuples
# class LossFields(NamedTuple):
#     epsilon: float = 1e-5
class Loss:
    def __init__(self, epsilon: float = 1e-5) -> None:
        self.__epsilon = epsilon

    @property
    def epsilon(self) -> float:
        return self.__epsilon
    
    @abstractmethod
    def loss(self, value: float) -> float:
        pass

    def gradient(self, value: float) -> float:
        return (self.loss(value + self.epsilon) -
                self.loss(value)) / self.epsilon


class TargetFields(NamedTuple):
    target: float
    low_penalty: float
    high_penalty: float


class Target(TargetFields, Loss):
    def loss(self, value: float) -> float:
        lack = self.target - value
        too_low = lack > 0
        return lack * (self.low_penalty if too_low else self.high_penalty)

    @staticmethod
    def make_symmetric(target: str, penalty: str) -> 'Target':
        return Target(float(target), float(penalty), float(penalty))

    @staticmethod
    def make_asymmetric(
            target: str, low_penalty: str, high_penalty) -> 'Target':
        return Target(float(target), float(low_penalty), float(high_penalty))

    @staticmethod
    def make_max_limit(limit: str, penalty: str) -> 'Target':
        return Target(float(limit), 0, float(penalty))

    @staticmethod
    def make_min_limit(limit: str, penalty: str) -> 'Target':
        return Target(float(limit), float(penalty), 0)


TYPES: Mapping[str, Callable] = {
    'target-sym': Target.make_symmetric,
    'target-asym': Target.make_asymmetric,
    'max': Target.make_max_limit,
    'min': Target.make_min_limit}
