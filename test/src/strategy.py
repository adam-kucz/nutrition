from typing import Optional

import hypothesis.strategies as st

from src.nutritional_info import NutrientInfo


def reals(*args, **kwargs) -> st.SearchStrategy[float]:
    kwargs.setdefault('allow_nan', False)
    kwargs.setdefault('allow_infinity', False)
    return st.floats(*args, **kwargs)


def nutrient_names(*args, **kwargs) -> st.SearchStrategy[str]:
    kwargs.setdefault('alphabet',
                      st.characters(blacklist_categories=('P', 'C')))
    return st.text(*args, **kwargs)


@st.composite
def nut_infos(draw, min_value: float = 0,
              max_value: Optional[float] = None,
              no_values: bool = False) -> NutrientInfo:
    names = draw(nutrient_names())  # pylint: disable=no-value-for-parameter
    if no_values:
        return NutrientInfo({name: 0 for name in names})
    return NutrientInfo(
        draw(st.fixed_dictionaries(
            {name: st.floats(min_value, max_value, allow_infinity=False)
             for name in names})))


# pylint: disable=no-value-for-parameter
st.register_type_strategy(NutrientInfo, nut_infos())
# pylint: enable=no-value-for-parameter
