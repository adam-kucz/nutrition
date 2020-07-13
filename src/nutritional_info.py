from collections import UserDict, defaultdict
from typing import (Union, overload, Mapping, Iterable, MutableMapping)

from funcy import merge_with, walk_values


class NutrientInfo(UserDict, MutableMapping[str, float]):
    def __init__(
            self,
            values: Union[Mapping[str, float], Iterable[str], None] = None)\
            -> None:
        self.data = {}  # for pylint
        if not isinstance(values, Mapping):
            values = {name: 0 for name in values or ()}
        super().__init__(defaultdict(lambda: 0, values))

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
            return sum(self[key] * value for key, value in multiplier)
        return NutrientInfo(walk_values(multiplier.__mul__, self))

    def __imul__(self, multiplier: float) -> 'NutrientInfo':
        self.data = walk_values(multiplier.__mul__, self.data)
        return self

    # def __str__(self) -> str:
    #     return (f"{self.__class__.__name__}("
    #             f"canonical names: {canonical_names or 'None'}, "
    #             f"values: {dict(self.internal)})")

    # def __repr__(self) -> str:
    #     return str(self)


VOID_NUTRIENT_INFO = NutrientInfo()
