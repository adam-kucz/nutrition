# pylint: disable=no-value-for-parameter
from typing import (
    Callable, Collection, List,
    NamedTuple, Optional, Tuple, Type, TypeVar, Union)

import hypothesis.strategies as st
from hypothesis import assume
from sympy import Expr, Add, Mul, Pow, Piecewise, Derivative  # type: ignore

from src.nutritional_info import Nutrient, NutrientInfo


def reals(*args, **kwargs) -> st.SearchStrategy[float]:
    kwargs.setdefault('min_value', 0)
    kwargs.setdefault('allow_nan', False)
    kwargs.setdefault('allow_infinity', False)
    return st.floats(*args, **kwargs)


@st.composite
def nutrients(draw, *args, **kwargs) -> Nutrient:
    kwargs.setdefault('alphabet',
                      st.characters(whitelist_categories=('L', 'N', 'Zs')))
    name = (draw(st.characters(whitelist_categories=('L',))) +
            draw(st.text(*args, **kwargs)))
    return Nutrient(name)


@st.composite
def nut_infos(draw, min_value: float = 0,
              max_value: Optional[float] = None,
              no_values: bool = False) -> NutrientInfo:
    symbols = draw(st.iterables(nutrients()))
    if no_values:
        return NutrientInfo(symbols)
    return NutrientInfo(
        draw(st.fixed_dictionaries(
            {sym: reals(min_value=min_value, max_value=max_value)
             for sym in symbols})))


S = TypeVar('S')
T = TypeVar('T')


@st.composite
def collections_with_elements(
        draw, num: int, collection: st.SearchStrategy[Collection[T]])\
        -> Tuple[Collection[T], Tuple[T, ...]]:
    col = draw(collection)
    assume(len(col) >= num)
    permuted = tuple(draw(st.permutations(list(col))))
    return col, permuted[:num]


def with_extra(value: S, strategy: st.SearchStrategy[T])\
        -> st.SearchStrategy[Union[T, S]]:
    return st.one_of(st.just(value), strategy)


def from_or_0(min_value: float = 0) -> st.SearchStrategy[float]:
    return with_extra(0, reals(min_value=min_value))


st.register_type_strategy(float, reals())
st.register_type_strategy(Nutrient, nutrients())
st.register_type_strategy(NutrientInfo, nut_infos())
# pylint: disable=no-member
st.register_type_strategy(
    Tuple[NutrientInfo, Nutrient],
    collections_with_elements(1, nut_infos())
    .map(lambda pair: (pair[0], pair[1][0])))
