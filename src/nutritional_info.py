import csv
from collections import defaultdict, UserDict
from itertools import chain
from pathlib import Path
from typing import (
    Optional, Collection, Union, overload, Mapping, MutableMapping)
from warnings import warn

from funcy import flip, walk_values, join_with, merge_with, first


class Translation(UserDict, Mapping[str, str]):
    def __init__(self, mapping: Optional[Mapping[str, str]] = None) -> None:
        mapping = mapping or {}
        self.canonical = set(mapping.values())
        for key, value in mapping.items():
            if key in self.canonical and key != value:
                raise ValueError(
                    f"Mapping {mapping} is invalid "
                    "as a basis for translation, "
                    f"name '{key}' occurs both as a canonical "
                    f"(in '{flip(dict(mapping))[key]}': '{key}') "
                    f"and non-canonical (in '{key}': '{value}') name")
        self.data = dict(mapping, **{key: key for key in self.canonical})

    def __getitem__(self, key: str):
        if key not in chain(self.data, self.canonical):
            warn(f"Unknown nutrient name: {key}")
        return self.data.get(key, key)

    @staticmethod
    def read(path: Path) -> 'Translation':
        names: MutableMapping[str, str] = {}
        lines = path.read_text().split('\n')
        for line in csv.reader(lines):
            if not line:
                continue
            key = line[0]
            names[key] = key
            for name in line[1:]:
                names[name] = key
        return Translation(names)

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"canonical: {self.canonical}, "
                f"dict: {self.data})")

    def __repr__(self) -> str:
        return str(self)

    # TODO: relax compatibility conditions
    def compatible_with(self, other: 'Translation') -> bool:
        return set(self.canonical) == set(other.canonical) and\
            not all(self[key] == other[key]
                    for key in self if key in other)

    def __add__(self, other: 'Translation') -> 'Translation':
        if not self.compatible_with(other):
            raise ValueError(
                "Cannot add incompatible translation: "
                f"{self} + {other}")
        return Translation(dict(chain(self.items(), other.items())))


class NutrientInfo(MutableMapping[str, float]):
    def __init__(self, translation: Union[Translation, 'NutrientInfo'],
                 values: Optional[Mapping[str, float]] = None) -> None:
        if isinstance(translation, NutrientInfo):
            nut_info, translation = translation, translation.translation
            values = merge_with(first, values or {}, nut_info.internal)
        self.__translation = translation
        canonical_values = join_with(
            sum,
            ({translation.get(key, key): value}
             for key, value in values.items()))\
            if values else {}
        self.__values: MutableMapping[str, float] = \
            defaultdict(lambda: 0, canonical_values)

    @property
    def translation(self) -> Translation:
        """Translation from arbitrary to canonical names"""
        return self.__translation

    @property
    def internal(self) -> Mapping[str, float]:
        """Internal representation of values on canonical names"""
        return self.__values

    @property
    def all_names(self) -> Collection[str]:
        """Get a list of all recognized nutrient names"""
        return set(*self.translation.keys(), *self.translation.canonical)

    def __iter__(self):
        return iter(self.internal)

    def __len__(self):
        return len(self.internal)

    def __getitem__(self, name: str) -> float:
        return self.internal[self.translation[name]]

    def __delitem__(self, name: str) -> None:
        del self.__values[self.translation[name]]

    def __setitem__(self, name: str, new_value: float) -> None:
        if name in self.all_names:
            self.__values[self.translation[name]] = new_value
        else:
            raise ValueError(f"{name} is not a known nutrient name")

    def __add__(self, other: 'NutrientInfo') -> 'NutrientInfo':
        """
        Combines two NutrientInfo object

        Merges translations of both NutrientInfo objects and
        adds values for the nutrients point-wise
        """
        new_translation = Translation(self.translation)
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
            self[self.translation[key]] += value
        return self

    @overload
    def __mul__(self, multiplier: float) -> 'NutrientInfo':
        ...

    @overload  # noqa: F811
    def __mul__(self, multiplier: 'NutrientInfo') -> float:
        ...

    def __mul__(self, multiplier):  # noqa: F811
        if isinstance(multiplier, NutrientInfo):
            return sum(self[key] * value for key, value in multiplier)
        return NutrientInfo(
            self.translation, walk_values(multiplier.__mul__, self.internal))

    def __imul__(self, multiplier: float) -> 'NutrientInfo':
        self.__values = walk_values(multiplier.__mul__, self.internal)
        return self

    def __str__(self) -> str:
        canonical_names = ", ".join(
            f"{name} -> {canonical}"
            for name, canonical in self.translation.items()
            if name != canonical)
        return (f"{self.__class__.__name__}("
                f"canonical names: {canonical_names or 'None'}, "
                f"values: {dict(self.internal)})")

    def __repr__(self) -> str:
        return str(self)


VOID_TRANSLATION = Translation()
VOID_NUTRIENT = NutrientInfo(VOID_TRANSLATION)
