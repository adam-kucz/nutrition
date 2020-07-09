from pathlib import Path

from hypothesis import given
import hypothesis.strategies as st

import test.src.base as base
from src.nutritional_info import NutrientInfo, read_translation


translation = st.builds(Translation, st.dictionaries())
nut_info = st.builds(NutrientInfo, )

class TestRead(base.AdvancedTestCase):
    def test_read_translation(self):
        filepath = \
            Path(__file__).parent.parent / "data" / "nutritional-info-test-1.csv"
        filecontent = (
            "potato,tomato,vegetable\n"
            "sugar,carbohydrate,starch\n"
            "salt\n"
            "\n"
            "water,h2o,H2O\n")
        filepath.write_text(filecontent)
        result = read_translation(filepath)
        expected = {
            'potato': 'potato',
            'tomato': 'potato',
            'vegetable': 'potato',
            'sugar': 'sugar',
            'carbohydrate': 'sugar',
            'starch': 'sugar',
            'salt': 'salt',
            'water': 'water',
            'h2o': 'water',
            'H2O': 'water'}
        self.assertCountEqual(result.items(), expected.items())


class TestNutrientInfo(base.AdvancedTestCase):
    def test_init(self):
        with self.assertRaises(Exception):
            NutrientInfo()

        translation = {'starch': 'carbohydrate',
                       'carbohydrate': 'carbohydrate',
                       'salt': 'salt'}
        basic = NutrientInfo(translation)
        self.assertEqual(basic.translation, translation)
        self.assertEqual(basic.internal, {})

        vals = {'carbohydrate': 4, 'salt': 2}
        alt_vals = {'starch': 4, 'salt': 2}
        from_vals = NutrientInfo(translation, vals)
        from_alt_vals = NutrientInfo(basic, alt_vals)
        self.assertAllEqual(
            from_vals.translation, from_alt_vals.translation, translation)
        self.assertAll(
            self.assertCountEqual,
            from_vals.internal.items(),
            from_alt_vals.internal.items(),
            vals.items())

    @given(nut_info)
    def test_copy_init(self, example: NutrientInfo):
        self.assertEqual(NutrientInfo(example), example)


    @given(nut_info())
    def test_add_unit(self,
                      translation: Mapping[str, str],
                      nut_info: NutritionalInfo):
        empty = NutrientInfo(translation)
        self.assertAllEqual(nut_info, nut_info + empty, empty + nut_info)
        old_nut_info = NutrientInfo()

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
