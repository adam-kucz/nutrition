from copy import deepcopy
from itertools import tee
from typing import Set, Mapping

from hypothesis import given, infer, reproduce_failure
import hypothesis.strategies as st

import test.src.base as base
import test.src.strategy as sty
from src.nutritional_info import NutrientInfo, VOID_NUTRIENT_INFO


class TestNutrientInfo(base.AdvancedTestCase):
    def test_init_default(self):
        self.assertEqual(NutrientInfo(), VOID_NUTRIENT_INFO)

    @given(names=infer)
    def test_init_iterable(self, names: Set[str]):
        nut_info = NutrientInfo(names)
        self.assertCountEqual(nut_info, names)
        for value in nut_info.values():
            self.assertEqual(value, 0)

    @given(mapping=st.dictionaries(st.text(), sty.reals()))
    def test_init_mapping(self, mapping: Mapping[str, float]):
        nut_info = NutrientInfo(mapping)
        self.assertCountEqual(nut_info, mapping.keys())
        for key, value in nut_info.items():
            self.assertEqual(value, mapping[key])

    @given(copy=infer)
    def test_copy_init(self, copy: NutrientInfo):
        original = deepcopy(copy)
        self.assertAllEqual(NutrientInfo(copy), original, copy)

    @given(nut_info=infer)
    def test_add_unit(self, nut_info: NutrientInfo):
        add_unit = VOID_NUTRIENT_INFO
        self.assertAllEqual(nut_info, nut_info + add_unit, add_unit + nut_info)

    # def test_numeric(self):
    #     alphabet = 'abcdef'
    #     translation = {letter: letter for letter in alphabet}

    #     def nth_info(n: int) -> NutrientInfo:
    #         return NutrientInfo(translation, {c: n for c in alphabet})

    #     empty = NutrientInfo(translation)
    #     zero = nth_info(0)
    #     one = nth_info(1)
    #     example0 = NutrientInfo(empty, {'a': 2, 'b': 3})
    #     example1 = NutrientInfo(empty, {c: ord(c)-ord('a') for c in alphabet})
    #     with self.subTest('addition'):
    #         with self.subTest('empty'):
    #             self.assertAllEqual(one, empty + one, one + empty)
    #             self.assertAllEqual(
    #                 example0, empty + example0, example0 + empty)
    #             self.assertAllEqual(
    #                 example1, empty + example1, example1 + empty)
    #         with self.subTest('adding ones'):
    #             for i in range(10):
    #                 with self.subTest(info=sum([one]*i, zero)):
    #                     self.assertEqual(sum([one]*i, zero), nth_info(i))
    #         # with self.subTest('general'):
    #             # self.assertEqual(nth_info(2) + example1, 
