import math
from collections import UserDict
from itertools import chain
from operator import mul
from typing import (Union, overload, Mapping, Iterable, MutableMapping)

from funcy import partial, merge_with, walk_values


class NutrientInfo(UserDict, MutableMapping[str, float]):
    def __init__(
            self,
            values: Union[Mapping[str, float], Iterable[str], None] = None)\
            -> None:
        self.data = {}  # for pylint
        if not isinstance(values, Mapping):
            values = {name: 0 for name in values or ()}
        super().__init__(values)

    def __missing__(self, _: str) -> float:
        return 0

    @staticmethod
    def constant(names: Iterable[str], value: float = 0):
        return NutrientInfo({name: value for name in names})

    def __add__(self, other: 'NutrientInfo') -> 'NutrientInfo':
        """
        Combines two NutrientInfo object

        Adds values for the nutrients point-wise
        """
        return NutrientInfo(merge_with(sum, self, other))

    def __iadd__(self, other: 'NutrientInfo') -> 'NutrientInfo':
        self.data = merge_with(sum, self, other)
        return self

    @overload
    def __mul__(self, multiplier: float) -> 'NutrientInfo':
        ...
    @overload  # noqa: F811, E301
    def __mul__(self, multiplier: 'NutrientInfo') -> float:
        ...

    def __mul__(self, multiplier):  # noqa: F811
        if isinstance(multiplier, NutrientInfo):
            return sum(self[key] * value for key, value in multiplier.items())
        return NutrientInfo(walk_values(partial(mul, multiplier), self.data))

    def __rmul__(self, multiplier: float):
        return self * multiplier

    def __imul__(self, multiplier: float) -> 'NutrientInfo':
        self.data = walk_values(multiplier.__mul__, self.data)
        return self

    def isclose(self, other: 'NutrientInfo',
                rel_tol: float = 1e-9, abs_tol: float = 0) -> bool:
        return all(math.isclose(self[key], other[key],
                                rel_tol=rel_tol, abs_tol=abs_tol)
                   for key in chain(self, other))

    # def __str__(self) -> str:
    #     return (f"{self.__class__.__name__}("
    #             f"canonical names: {canonical_names or 'None'}, "
    #             f"values: {dict(self.internal)})")

    # def __repr__(self) -> str:
    #     return str(self)


VOID_NUTRIENT_INFO = NutrientInfo()
