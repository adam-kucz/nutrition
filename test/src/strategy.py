from typing import Optional, Dict

import hypothesis as hyp
import hypothesis.strategies as st

from src.nutritional_info import Translation, NutrientInfo


@st.composite
def translations(
        draw, include_canonical: bool = False)\
        -> Translation:
    nutrient_name = st.text(st.characters(blacklist_categories=('P', 'C')))
    mapping = draw(st.dictionaries(nutrient_name, nutrient_name))
    if include_canonical:
        mapping.update({key: key for key in mapping.values()})
    hyp.assume(all(key not in mapping.values() or key == value
                   for key, value in mapping.items()))
    return Translation(mapping)


@st.composite
def nut_infos(draw, min_value: float = 0,
              max_value: Optional[float] = None,
              no_values: bool = False) -> NutrientInfo:
    trans = draw(translations())  # pylint: disable=no-value-for-parameter
    if no_values:
        return NutrientInfo(trans)
    values = draw(st.fixed_dictionaries(
        {key: st.floats(min_value, max_value, allow_infinity=False)
         for key in trans.canonical}))
    return NutrientInfo(trans, values)


# pylint: disable=no-value-for-parameter
st.register_type_strategy(Translation, translations())
st.register_type_strategy(NutrientInfo, nut_infos())
# pylint: enable=no-value-for-parameter
