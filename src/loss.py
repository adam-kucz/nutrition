import csv
from abc import abstractmethod
from pathlib import Path
from typing import Callable, Mapping, List, NamedTuple, Union

from nutritional_info import NutrientInfo

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
    def loss(self, value: NutrientInfo) -> float:
        pass

    def gradient(self, nutrient_info: NutrientInfo) -> NutrientInfo:
        current = self.loss(nutrient_info)

        def single_gradient(key: str, old_value: float):
            new_info = dict(nutrient_info)
            new_info.update({key: old_value * (1 + self.epsilon)})
            return (self.loss(new_info) -
                    current) / (self.epsilon * old_value)
        return {key: single_gradient(key, value)
                for key, value in nutrient_info.items()}


class TargetFields(NamedTuple):
    key: str
    target: float
    low_penalty: float
    high_penalty: float


class Target(TargetFields, Loss):
    def loss(self, value: NutrientInfo) -> float:
        lack = self.target - value[self.key]
        too_low = lack > 0
        return lack * (self.low_penalty if too_low else self.high_penalty)

    @staticmethod
    def make_symmetric(key: str, target: str,
                       penalty: Union[str, int] = 1) -> 'Target':
        return Target(key, float(target), float(penalty), float(penalty))

    @staticmethod
    def make_asymmetric(key: str, target: str,
                        low_penalty: str, high_penalty) -> 'Target':
        return Target(key, float(target),
                      float(low_penalty), float(high_penalty))

    @staticmethod
    def make_max_limit(key: str, limit: str,
                       penalty: Union[str, int] = 1) -> 'Target':
        return Target(key, float(limit), 0, float(penalty))

    @staticmethod
    def make_min_limit(key: str, limit: str,
                       penalty: Union[str, int] = 1) -> 'Target':
        return Target(key, float(limit), float(penalty), 0)


class RelativeTargetFields(NamedTuple):
    key: str
    comparison: str
    multiplier: float
    low_penalty: float
    high_penalty: float


CALORIC_VALUE: Mapping[str, float] = {
    'carbohydrate': 4,
    'protein': 4,
    'sugar': 4,
    'fat': 9,
    'saturated': 9}


class RelativeTarget(RelativeTargetFields, Loss):
    def loss(self, value: NutrientInfo) -> float:
        lack = self.multiplier * value[self.comparison] - value[self.key]
        too_low = lack > 0
        return lack * (self.low_penalty if too_low else self.high_penalty)

    @staticmethod
    def make_symmetric(key: str, comparison: str, multiplier: str,
                       penalty: Union[str, int] = 1) -> 'RelativeTarget':
        return RelativeTarget(
            key, comparison, float(multiplier), float(penalty), float(penalty))

    @staticmethod
    def make_asymmetric(key: str, comparison: str, multiplier: str,
                        low_penalty: str, high_penalty) -> 'RelativeTarget':
        return RelativeTarget(key, comparison, float(multiplier),
                              float(low_penalty), float(high_penalty))

    @staticmethod
    def make_max_limit(key: str, comparison: str, multiplier: str,
                       penalty: Union[str, int] = 1) -> 'RelativeTarget':
        return RelativeTarget(key, comparison, float(multiplier),
                              0, float(penalty))

    @staticmethod
    def make_min_limit(key: str, comparison: str, multiplier: str,
                       penalty: Union[str, int] = 1) -> 'RelativeTarget':
        return RelativeTarget(key, comparison, float(multiplier),
                              float(penalty), 0)

    @staticmethod
    def make_max_energy_fraction(
            key: str, fraction: str,
            penalty: Union[str, int] = 1) -> 'RelativeTarget':
        return RelativeTarget(
            key, 'energy', float(fraction) / CALORIC_VALUE[key],
            float(penalty), 0)

    @staticmethod
    def make_sym_energy_fraction(
            key: str, fraction: str,
            penalty: Union[str, int] = 1) -> 'RelativeTarget':
        return RelativeTarget(
            key, 'energy', float(fraction) / CALORIC_VALUE[key],
            float(penalty), float(penalty))


TYPES: Mapping[str, Callable[..., Loss]] = {
    'target-sym': Target.make_symmetric,
    'target-asym': Target.make_asymmetric,
    'max': Target.make_max_limit,
    'min': Target.make_min_limit,
    'relative-max': RelativeTarget.make_max_energy_fraction,
    'target-relative-sym': RelativeTarget.make_sym_energy_fraction,
    'target-relative-to-sym': RelativeTarget.make_symmetric,
    'target-relative-to-asym': RelativeTarget.make_asymmetric}


def read_reference(source: Path) -> List[Loss]:
    losses = []
    lines = source.read_text().split('\n')
    for line in csv.reader(lines):
        if not line:
            continue
        nutrient = line[0]
        loss_type = line[1] or 'target-sym'
        losses.append(TYPES[loss_type](nutrient, *line[2:]))
    return losses
