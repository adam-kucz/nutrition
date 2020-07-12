from pathlib import Path

from hypothesis import given, infer
# import hypothesis.strategies as st

import test.src.base as base
import test.src.strategy as sty
from src.nutritional_info import NutrientInfo, Translation


class TestTranslation(base.AdvancedTestCase):
    def test_translation_read(self):
        filepath = \
            Path(__file__).parent.parent / "data" / "nutritional-info-test-1.csv"
        filecontent = (
            "potato,tomato,vegetable\n"
            "sugar,carbohydrate,starch\n"
            "salt\n"
            "\n"
            "water,h2o,H2O\n")
        filepath.write_text(filecontent)
        result = Translation.read(filepath)
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

    @given(sty.translations())  # pylint: disable=no-value-for-parameter
    def test_translation_with_canonical(self, tr: Translation) -> None:
        for value in tr.canonical:
            self.assertIn(value, tr.values())

    @given(tr=infer)
    def test_translation_create(self, tr: Translation) -> None:
        self.assertCountEqual(tr.canonical, set(tr.values()))


class TestNutrientInfo(base.AdvancedTestCase):
    def test_init(self):
        with self.assertRaises(Exception):
            NutrientInfo()  # pylint: disable=no-value-for-parameter

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

    @given(example=infer)
    def test_copy_init(self, example: NutrientInfo):
        self.assertEqual(NutrientInfo(example), example)

    @given(translation=infer, nut_info=infer)
    def test_add_unit(self,
                      translation: Translation,
                      nut_info: NutrientInfo):
        empty = NutrientInfo(translation)
        zero = NutrientInfo(empty, {k: 0 for k in translation.canonical})
        self.assertAllEqual(nut_info, nut_info + empty, empty + nut_info,
                            nut_info + zero, zero + nut_info)
        old_nut_info = NutrientInfo(nut_info)
        nut_info += empty
        self.assertEqual(nut_info, old_nut_info)

    @given(nut_info_0=infer, nut_info_1=infer)
    def test_add_commutative(
            self, nut_info_0: NutrientInfo, nut_info_1: NutrientInfo):
        self.assertEqual(nut_info_0 + nut_info_1, nut_info_1 + nut_info_0)

    @given(nut_info_0=infer, nut_info_1=infer, nut_info_2=infer)
    def test_add_associative(self,
                             nut_info_0: NutrientInfo,
                             nut_info_1: NutrientInfo,
                             nut_info_2: NutrientInfo):
        self.assertEqual(
            (nut_info_0 + nut_info_1) + nut_info_2,
            nut_info_0 + (nut_info_1 + nut_info_2))
