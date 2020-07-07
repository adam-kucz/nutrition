import csv
from collections import defaultdict
from pathlib import Path
from typing import Mapping, MutableMapping, Optional, Tuple, Union, overload

from funcy import walk_values

Translation = Mapping[str, str]


def read_translation(path: Path) -> Translation:
    names: MutableMapping[str, str] = {}
    lines = path.read_text().split('\n')
    for line in csv.reader(lines):
        if not line:
            continue
        key = line[0]
        names[key] = key
        for name in line[1:]:
            names[name] = key
    return names


class NutrientInfo(MutableMapping[str, float]):
    def __init__(self, translation: Union[Translation, 'NutrientInfo'],
                 values: Optional[Mapping[str, float]] = None) -> None:
        if isinstance(translation, NutrientInfo):
            if values is not None:
                cls = self.__class__.__name__
                raise ValueError(
                    f"{cls} does not accept a second argument "
                    "if the first one is a {cls} object")
            nut_info = translation
            translation = nut_info.translation
            values = nut_info.internal
        self.__translation = dict(translation)
        self.__values: MutableMapping[str, float] = \
            defaultdict(lambda: 0, values or {})

    @property
    def translation(self) -> Translation:
        """Translation from arbitrary to canonical names"""
        return self.__translation

    @property
    def internal(self) -> MutableMapping[str, float]:
        """Internal representation of values on canonical names"""
        return self.__values

    def canonical_name(self, name: str) -> str:
        """Get canonical name for 'name'"""
        return self.translation.get(name, name)

    @property
    def all_names(self) -> Tuple[str, ...]:
        """Get a list of all recognized nutrient names"""
        return tuple(self.translation.keys())

    def __iter__(self):
        return iter(self.internal)

    def __len__(self):
        return len(self.internal)

    def __getitem__(self, name: str) -> float:
        return self.internal[self.canonical_name(name)]

    def __delitem__(self, name: str) -> None:
        del self.internal[self.canonical_name(name)]

    def __setitem__(self, name: str, new_value: float) -> None:
        if name in self.all_names:
            self.internal[self.canonical_name(name)] = new_value
        else:
            raise ValueError(f"{name} is not a known nutrient name")

    def __add__(self, other: 'NutrientInfo') -> 'NutrientInfo':
        """
        Combines two NutrientInfo object

        Merges translations of both NutrientInfo objects and
        adds values for the nutrients point-wise
        """
        new_translation = dict(self.translation)
        try:
            for key, name in other.translation.items():
                if key not in new_translation:
                    new_translation[key] = new_translation.get(name, name)
        except AttributeError:
            for key in other:
                if key not in new_translation:
                    new_translation[key] = key
        new_values = defaultdict(lambda: 0, self.internal)
        for key, value in other.items():
            new_values[new_translation.get(key, key)] += value
        return NutrientInfo(new_translation, new_values)

    def __iadd__(self, other: 'NutrientInfo') -> 'NutrientInfo':
        for key, value in other.items():
            self[self.canonical_name(key)] += value
        return self

    @overload
    def __mul__(self, multiplier: float) -> 'NutrientInfo':
        ...
    @overload
    def __mul__(self, multiplier: 'NutrientInfo') -> float:
        ...

    def __mul__(self, multiplier):
        if isinstance(multiplier, NutrientInfo):
            return sum(self[key] * value for key, value in multiplier)
        return NutrientInfo(
            self.translation, walk_values(multiplier.__mul__, self.internal))

    def __imul__(self, multiplier: float) -> 'NutrientInfo':
        self.__values = walk_values(multiplier.__mul__, self.internal)
        return self


VOID_NUTRIENT = NutrientInfo({})
