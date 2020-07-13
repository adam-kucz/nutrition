import math
from copy import deepcopy
from itertools import chain
from typing import Set, Mapping, List, Iterable

import hypothesis.strategies as st
from hypothesis import given, infer, assume, reproduce_failure

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

    @given(names=infer, value=sty.reals())
    def test_constant(self, names: Iterable[str], value: float):
        for value_1 in NutrientInfo.constant(names, value).values():
            self.assertEqual(value, value_1)

    @given(nut_info=infer)
    def test_add_unit(self, nut_info: NutrientInfo):
        add_unit = VOID_NUTRIENT_INFO
        self.assertAllEqual(nut_info, nut_info + add_unit, add_unit + nut_info)

    @given(nut_info_0=infer, nut_info_1=infer)
    def test_add_commutative(
            self, nut_info_0: NutrientInfo, nut_info_1: NutrientInfo):
        self.assertTrue(NutrientInfo.isclose(
            nut_info_0 + nut_info_1,
            nut_info_1 + nut_info_0))

    @given(nut_info_0=infer, nut_info_1=infer, nut_info_2=infer)
    def test_add_associative(self,
                             nut_info_0: NutrientInfo,
                             nut_info_1: NutrientInfo,
                             nut_info_2: NutrientInfo):
        self.assertTrue(NutrientInfo.isclose(
            (nut_info_0 + nut_info_1) + nut_info_2,
            nut_info_0 + (nut_info_1 + nut_info_2)))

    @given(names=infer, value_0=sty.reals(), value_1=sty.reals())
    def test_add_constant(
            self, names: List[str], value_0: float, value_1: float):
        self.assertTrue(NutrientInfo.isclose(
            NutrientInfo.constant(names, value_0) +
            NutrientInfo.constant(names, value_1),
            NutrientInfo.constant(names, value_0 + value_1)))

    @given(nut_info_0=infer, nut_info_1=infer)
    def test_add_general(
            self, nut_info_0: NutrientInfo, nut_info_1: NutrientInfo):
        nut_info_2 = nut_info_0 + nut_info_1
        for key in chain(nut_info_0, nut_info_1):
            self.assertIn(key, nut_info_2)
            self.assertAlmostEqual(nut_info_0[key] + nut_info_1[key],
                                   nut_info_2[key])

    @given(nut_info_0=infer, nut_info_1=infer)
    def test_iadd(
            self, nut_info_0: NutrientInfo, nut_info_1: NutrientInfo):
        nut_info_0_copy = deepcopy(nut_info_0)
        nut_info_0 += nut_info_1
        self.assertEqual(nut_info_0, nut_info_0_copy + nut_info_1)

    @given(nut_info=infer, mul=sty.reals())
    def test_mul_float_basic(self, nut_info: NutrientInfo, mul: float):
        self.assertEqual(nut_info * 0, NutrientInfo(nut_info.keys()))
        self.assertTrue(NutrientInfo.isclose(nut_info * mul, mul * nut_info))

    @given(nut_info=infer, mul0=sty.reals(), mul1=sty.reals())
    def test_mul_float_associative(
            self, nut_info: NutrientInfo, mul0: float, mul1: float):
        for val in nut_info.values():
            assume(math.isclose((val * mul0) * mul1, val * (mul0 * mul1)))
        self.assertTrue(NutrientInfo.isclose(
            nut_info * (mul0 * mul1), (nut_info * mul0) * mul1))

    @given(nut_info=infer, mul0=sty.reals(), mul1=sty.reals())
    def test_mul_float_distributive_second(
            self, nut_info: NutrientInfo, mul0: float, mul1: float):
        for val in nut_info.values():
            assume(math.isclose(val * (mul0 + mul1), val * mul0 + val * mul1))
        self.assertTrue(NutrientInfo.isclose(
            nut_info * (mul0 + mul1),
            nut_info * mul0 + nut_info * mul1))

    @given(nut_info0=infer, nut_info1=infer, mul=sty.reals())
    def test_mul_float_distributive_first(
            self, nut_info0: NutrientInfo, nut_info1: NutrientInfo,
            mul: float):
        for key in chain(nut_info0, nut_info1):
            val0, val1 = nut_info0[key], nut_info1[key]
            assume(math.isclose((val0 + val1) * mul, val0 * mul + val1 * mul))
        self.assertTrue(NutrientInfo.isclose(
            (nut_info0 + nut_info1) * mul,
            nut_info0 * mul + nut_info1 * mul))

    @given(nut_info0=infer, nut_info1=infer, nut_info2=infer)
    def test_dot(self,
                 nut_info0: NutrientInfo,
                 nut_info1: NutrientInfo,
                 nut_info2: NutrientInfo):
        self.assertEqual(VOID_NUTRIENT_INFO * nut_info0, 0)
        self.assertTrue(math.isclose(
            nut_info0 * NutrientInfo.constant(nut_info0.keys(), 1),
            sum(nut_info0.values())))
        self.assertTrue(math.isclose(
            nut_info0 * nut_info1, nut_info1 * nut_info0))
        self.assertTrue(math.isclose(
            (nut_info0 + nut_info1) * nut_info2,
            nut_info0 * nut_info2 + nut_info1 * nut_info2))

    @given(nut_info=infer, multiplier=sty.reals())
    def test_imul(self, nut_info: NutrientInfo, multiplier: float):
        nut_info_copy = deepcopy(nut_info)
        nut_info *= multiplier
        self.assertEqual(nut_info, nut_info_copy * multiplier)

    @given(nut_info=infer, delta=st.floats(min_value=1e-13,
                                           allow_infinity=False))
    def test_isclose(self, nut_info: NutrientInfo, delta: float):
        self.assertTrue(NutrientInfo.isclose(nut_info, nut_info))
        for val in nut_info.values():
            assume(math.isfinite(val * (1 + delta * 0.95)))
        self.assertTrue(NutrientInfo.isclose(
            nut_info, nut_info * (1 + delta * 0.95), rel_tol=delta))
        if any(value != 0 for value in nut_info.values()):
            for val in nut_info.values():
                assume(math.isfinite(val * (1 + delta * 1.05)))
                if val != 0:
                    assume(math.isclose(
                        (val * (1 + delta * 1.05)) / val,
                        1 + delta * 1.05,
                        rel_tol=0,
                        abs_tol=0.03*delta))
            self.assertFalse(NutrientInfo.isclose(
                nut_info, nut_info * (1 + delta * 1.05),
                rel_tol=delta/(1 + delta * 1.05), abs_tol=0))
        for val in nut_info.values():
            assume(math.isfinite(val + delta * 0.95))
        self.assertTrue(NutrientInfo.isclose(
            nut_info, nut_info + NutrientInfo.constant(nut_info, delta * 0.95),
            abs_tol=delta))
        if nut_info:
            for val in nut_info.values():
                assume(math.isfinite(val + delta * 1.05))
                assume(math.isclose(
                    (val + delta * 1.05) - val,
                    delta * 1.05,
                    rel_tol=0,
                    abs_tol=0.03*delta))
            self.assertFalse(NutrientInfo.isclose(
                nut_info,
                nut_info + NutrientInfo.constant(nut_info, delta * 1.05),
                rel_tol=0,
                abs_tol=delta))

