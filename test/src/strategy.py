from typing import Optional

import hypothesis.strategies as st
from sympy import Symbol  # type: ignore

from src.nutritional_info import NutrientInfo


def reals(*args, **kwargs) -> st.SearchStrategy[float]:
    kwargs.setdefault('allow_nan', False)
    kwargs.setdefault('allow_infinity', False)
    return st.floats(*args, **kwargs)


def nutrients(*args, **kwargs) -> st.SearchStrategy[Symbol]:
    kwargs.setdefault('alphabet',
                      st.characters(blacklist_categories=('P', 'C')))
    return st.builds(Symbol, st.text(*args, **kwargs))


@st.composite
def nut_infos(draw, min_value: float = 0,
              max_value: Optional[float] = None,
              no_values: bool = False) -> NutrientInfo:
    # pylint: disable=no-value-for-parameter
    symbols = draw(st.iterables(nutrients()))
    # pylint: enable=no-value-for-parameter
    if no_values:
        return NutrientInfo(symbols)
    return NutrientInfo(
        draw(st.fixed_dictionaries(
            {sym: st.floats(min_value, max_value, allow_infinity=False)
             for sym in symbols})))


# pylint: disable=no-value-for-parameter
st.register_type_strategy(Symbol, nutrients())
st.register_type_strategy(NutrientInfo, nut_infos())
# pylint: enable=no-value-for-parameter
