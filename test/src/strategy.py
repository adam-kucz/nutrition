from typing import Optional, Dict

import hypothesis.strategies as st

from src.nutritional_info import Translation, NutrientInfo


def translations(
        include_canonical: bool = False) -> st.SearchStrategy[Translation]:
    nutrient_name = st.text(st.characters(blacklist_categories=('P', 'C')))
    map_strategy = st.dictionaries(nutrient_name, nutrient_name)
    if include_canonical:
        def add_canonical(dictionary: Dict[str, str]) -> Dict[str, str]:
            new_dict = dict(dictionary)
            new_dict.update({key: key for key in dictionary})
            return new_dict
        map_strategy = map_strategy\
            .map(add_canonical)\
            .filter(lambda d: all(key not in d.values() or key == value
                                  for key, value in d.items()))
    return st.builds(Translation, map_strategy)


def nut_infos(min_value: float = 0,
              max_value: Optional[float] = None,
              no_values: bool = False) -> st.SearchStrategy[NutrientInfo]:
    if no_values:
        return st.builds(NutrientInfo, translations())
    return translations().flatmap(
        lambda trans: st.builds(
            NutrientInfo,
            trans,
            st.fixed_dictionaries(
                {key: st.floats(min_value, max_value, allow_infinity=False)
                 for key in trans.canonical})))


st.register_type_strategy(Translation, translations())
st.register_type_strategy(NutrientInfo, nut_infos())
