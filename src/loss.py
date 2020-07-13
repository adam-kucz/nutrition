import csv
from abc import abstractmethod
from pathlib import Path
from typing import Callable, Mapping, List, NamedTuple, Union
from warnings import warn

from sympy import Expr
from .nutritional_info import NutrientInfo


Gradient = NutrientInfo


# TODO: figure out a standardized way of combining two NamedTuples
# class LossFields(NamedTuple):
#     epsilon: float = 1e-5
class Loss:
    def __init__(self, epsilon: float = 1e-5) -> None:
        if epsilon <= 0:
            raise ValueError(
                "Cannot use nonpositive epsilon of {epsilon} "
                "to compute gradients")
        self.__epsilon = epsilon

    @property
    def epsilon(self) -> float:
        return self.__epsilon
    
    @abstractmethod
    def loss(self, value: NutrientInfo) -> float:
        pass

    def gradient(self, nutrient_info: NutrientInfo) -> Gradient:
        current = self.loss(nutrient_info)

        def single_gradient(key: str, old_value: float):
            new_info = NutrientInfo(nutrient_info)
            new_info[key] = old_value * (1 + self.epsilon) if old_value else self.epsilon
            return (self.loss(new_info) -
                    current) / (self.epsilon * old_value)
        return NutrientInfo(
            {key: single_gradient(key, value)
             for key, value in nutrient_info.items()})


class AlgebraicLoss(Loss):
    def __init__(self, expr: Expr, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if expr.free_symbols():
            pass
        self.expression = expr

    def loss(self, value: NutrientInfo) -> float:
        return 0


class TargetFields(NamedTuple):
    key: str
    target: float
    low_penalty: float
    high_penalty: float


class Target(TargetFields, Loss):
    def loss(self, value: NutrientInfo) -> float:
        lack = self.target - value[self.key]
        too_low = lack > 0
        return lack * (
            self.low_penalty if too_low else self.high_penalty)

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


CALORIC_VALUE: NutrientInfo = NutrientInfo({
    'carbohydrate': 4,
    'protein': 4,
    'sugar': 4,
    'fat': 9,
    'saturated': 9})


class RelativeTarget(RelativeTargetFields, Loss):
    def loss(self, value: NutrientInfo) -> float:
        lack = self.multiplier * value[self.comparison] - value[self.key]
        too_low = lack > 0
        return lack * (
            self.low_penalty if too_low else self.high_penalty)

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
        if key not in CALORIC_VALUE:
            raise ValueError(f"Unknown caloric value for '{key}'")
        return RelativeTarget(
            key, 'energy', float(fraction) / CALORIC_VALUE[key],
            float(penalty), 0)

    @staticmethod
    def make_sym_energy_fraction(
            key: str, fraction: str,
            penalty: Union[str, int] = 1) -> 'RelativeTarget':
        if key not in CALORIC_VALUE:
            raise ValueError(f"Unknown caloric value for '{key}'")
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
        nutrient, loss_type, *args = line
        loss_type = loss_type or 'target-sym'
        losses.append(TYPES[loss_type](nutrient, *args))
    return losses


def read_all_references(source: Path) -> Mapping[str, List[Loss]]:
    losses = {}
    lines = source.read_text().split('\n')
    for line in csv.reader(lines):
        if not line:
            continue
        name, pathname, *rest = line
        if rest:
            warn(f"Unexpected values: {rest}")
        losses[name] = read_reference(Path(pathname))
    return losses
