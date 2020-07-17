import csv
from abc import abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import (
    Type, Callable, Mapping, List, Set, Union, MutableMapping)
from warnings import warn

from funcy import cached_readonly  # type: ignore
from sympy import (  # type: ignore
    sympify, S,
    Symbol, Expr, Derivative, Piecewise, Lambda, Dummy)

from .nutritional_info import NutrientInfo, CALORIC_VALUE, ENERGY

Gradient = NutrientInfo


class StrOrType:
    def __getattr__(self, typ: Type) -> Type:
        return Union[str, typ]


StrOr = StrOrType()


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
    def __init__(self, expr, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__expression = sympify(expr)

    def subs(self, *args, **kwargs) -> 'AlgebraicLoss':
        return AlgebraicLoss(self.expression.subs(*args, **kwargs))

    @property
    def expression(self) -> Expr:
        return self.__expression
        
    @cached_readonly
    def grad_exprs(self) -> Mapping[Symbol, Expr]:
        return defaultdict(
            lambda: S.Zero,
            {symbol: Derivative(self.expression, symbol)
             for symbol in self.symbols})

    def __eq__(self, other: object) -> bool:
        return (self.expression == other.expression
                if isinstance(other, AlgebraicLoss)
                else NotImplemented)

    def __hash__(self) -> int:
        return hash(self.expression)

    @cached_readonly
    def symbols(self) -> Set[Symbol]:
        return self.expression.free_symbols

    def ensure_sufficient(self, value: NutrientInfo) -> None:
        for symbol in self.symbols:
            if symbol not in value:
                raise ValueError(f"No value for '{symbol}' in {value}")

    def loss(self, value: NutrientInfo) -> float:
        self.ensure_sufficient(value)
        return float(self.expression.subs(value))

    def gradient(self, value: NutrientInfo) -> Gradient:
        self.ensure_sufficient(value)
        grad: MutableMapping[Symbol, float] = defaultdict(lambda: 0)
        for symbol in value:
            grad[symbol] = float(self.grad_exprs[symbol].subs(value))
        return Gradient(grad)

    def __str__(self) -> str:
        return f"AlgebraicLoss(expression={self.expression})"

    def __repr__(self) -> str:
        return str(self)


class Target(AlgebraicLoss):
    def __init__(self, expr, target, low_penalty, high_penalty) -> None:
        expr, target, low_penalty, high_penalty =\
            sympify((expr, target, low_penalty, high_penalty))
        if not callable(low_penalty):
            low_penalty = Lambda(Dummy(), low_penalty)
        if not callable(high_penalty):
            high_penalty = Lambda(Dummy(), high_penalty)

        lack: Expr = abs(expr - target)
        expression = lack *\
            Piecewise((low_penalty(lack), expr < target),
                      (high_penalty(lack), True))
        super().__init__(expression)

    @staticmethod
    def symmetric(key: StrOr(Symbol), target: Union[str, float],
                  penalty: Union[str, float] = 1) -> 'Target':
        return Target(key, target, penalty, penalty)

    @staticmethod
    def max_limit(key: StrOr(Symbol), limit: Union[str, float],
                  penalty: Union[str, float] = 1) -> 'Target':
        return Target(key, limit, 0, penalty)

    @staticmethod
    def min_limit(key: StrOr(Symbol), limit: Union[str, float],
                  penalty: Union[str, float] = 1) -> 'Target':
        return Target(key, limit, penalty, 0)

    @staticmethod
    def relative(
            key: StrOr(Symbol), comparison: StrOr(Symbol),
            multiplier: Union[str, float],
            low_penalty: Union[str, float],
            high_penalty: Union[str, float]) -> 'Target':
        target = sympify(multiplier) * sympify(comparison)
        return Target(key, target, low_penalty, high_penalty)

    @staticmethod
    def relative_symmetric(
            key: StrOr(Symbol), comparison: StrOr(Symbol),
            multiplier: Union[str, float], penalty: Union[str, float] = 1)\
            -> 'Target':
        return Target.relative(key, comparison, multiplier, penalty, penalty)

    @staticmethod
    def relative_max_limit(
            key: StrOr[Symbol], comparison: Union[Symbol, str],
            multiplier: Union[float, str], penalty: Union[float, str] = 1)\
            -> 'Target':
        return Target.relative(key, comparison, multiplier, 0, penalty)

    @staticmethod
    def relative_min_limit(key: str, comparison: str, multiplier: str,
                           penalty: str = '1') -> 'Target':
        return Target.relative(key, comparison, multiplier, penalty, 0)

    @staticmethod
    def max_energy_fraction(
            key: str, fraction: str,
            penalty: Union[str, float] = 1) -> 'Target':
        key = sympify(key)
        if key not in CALORIC_VALUE:
            raise ValueError(f"Unknown caloric value for '{key}'")
        multiplier = sympify(fraction) / CALORIC_VALUE[key]
        return Target.relative(key, ENERGY, multiplier, penalty, 0)

    @staticmethod
    def energy_fraction(
            key: str, fraction: str,
            penalty: Union[str, float] = 1) -> 'Target':
        key = sympify(key)
        if key not in CALORIC_VALUE:
            raise ValueError(f"Unknown caloric value for '{key}'")
        multiplier = sympify(fraction) / CALORIC_VALUE[key]
        return Target.relative(key, ENERGY, multiplier, penalty, penalty)


TYPES: Mapping[str, Callable[..., Loss]] = {
    'target-sym': Target.symmetric,
    'target-asym': Target,
    'max': Target.max_limit,
    'min': Target.min_limit,
    'relative-max': Target.max_energy_fraction,
    'target-relative-sym': Target.energy_fraction,
    'target-relative-to-sym': Target.relative_symmetric,
    'target-relative-to-asym': Target.relative}


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
