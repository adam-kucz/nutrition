import math
import unittest
from collections import ChainMap
from typing import Tuple

from hypothesis import given, settings, infer, assume
from hypothesis.strategies as st
from sympy import sympify, Symbol, Expr  # type: ignore

import test.src.base as base
import test.src.strategy as sty
from src.nutritional_info import NutrientInfo, CALORIC_VALUE
from src.loss import AlgebraicLoss, Target, Gradient


class TestLoss(base.AdvancedTestCase):
    @given(const=infer, nut_info=infer)
    def test_constant(self, const: float, nut_info: NutrientInfo):
        loss = AlgebraicLoss(const)
        self.assertEqual(loss.loss(nut_info), const)
        self.assertEqual(loss.gradient(nut_info),
                         NutrientInfo(nut_info.keys()))

    # pylint: disable=no-value-for-parameter
    @given(const=infer, data=infer)
    def test_linear(self, const: float, data: Tuple[NutrientInfo, Nutrient]):
        nut_info, key = data
        loss = AlgebraicLoss(sympify(const) * sympify(key))
        self.assertEqual(loss.loss(nut_info), const * nut_info[key])
        grad = NutrientInfo(nut_info.keys())
        grad[key] = const
        self.assertEqual(loss.gradient(nut_info), grad)

    @given(data=infer, target=infer, low_penalty=infer, high_penalty=infer)
    def test_target_grad(
            self, data: Tuple[NutrientInfo, Nutrient],
            target: float, low_penalty: float, high_penalty: float):
        nut_info, key = data
        loss = Target(key, target, low_penalty, high_penalty)
        grad = loss.gradient(nut_info)
        if nut_info[key] < target:
            self.assertEqual(grad[key], -low_penalty)
        elif nut_info[key] > target:
            self.assertEqual(grad[key], high_penalty)
        else:
            self.assertEqual(grad[key], 0)
        for other_key in nut_info:
            if other_key == key:
                continue
            self.assertEqual(grad[other_key], 0)

    @given(data=infer, target=infer,
           low_penalty=sty.from_or_0(1e-5), high_penalty=sty.from_or_0(1e-5))
    def test_target_loss(
            self, data: Tuple[NutrientInfo, Nutrient],
            target: float, low_penalty: float, high_penalty: float):
        nut_info, key = data
        assume(not math.isclose(nut_info[key], target))
        assume(not math.isclose(high_penalty, 0))
        assume(not math.isclose(low_penalty, 0))
        loss = Target(key, target, low_penalty, high_penalty)
        self.assertNotEqual(loss.loss(nut_info), 0)
        nut_info[key] = target
        self.assertEqual(loss.loss(nut_info), 0)

    @given(data=infer, target=sty.reals(max_value=1e50),
           delta=sty.reals(exclude_min=True, max_value=1e50),
           penalty=sty.from_or_0(1e-5))
    def test_target_symmetric(self, data: Tuple[NutrientInfo, Nutrient],
                              target: float, delta: float, penalty: float):
        assume(delta > 1e-10 * target)
        nut_info, key = data
        loss = Target.symmetric(key, target, penalty)
        grad = loss.gradient(nut_info)
        self.assertIn(grad[key], (-penalty, 0, penalty))
        for other_key in nut_info:
            if other_key != key:
                self.assertEqual(grad[other_key], 0)
        nut_info0 = NutrientInfo(nut_info)
        nut_info0[key] = target + delta
        self.assertAlmostEqual(loss.loss(nut_info0), delta*penalty,
                               delta=self.epsilon*delta*penalty)
        self.assertEqual(loss.gradient(nut_info0)[key], penalty)
        if delta < target:
            nut_info0[key] = target - delta
            self.assertAlmostEqual(loss.loss(nut_info0), delta*penalty,
                                   delta=self.epsilon*delta*penalty)
            self.assertEqual(loss.gradient(nut_info0)[key], -penalty)

    @given(data=infer, limit=infer, penalty=sty.from_or_0(1e-5))
    def test_target_max_limit(self, data: Tuple[NutrientInfo, Nutrient],
                              limit: float, penalty: float):
        nut_info, key = data
        loss = Target.max_limit(key, limit, penalty)
        grad = loss.gradient(nut_info)
        if nut_info[key] <= limit:
            self.assertEqual(loss.loss(nut_info), 0)
            self.assertEqual(grad, Gradient(nut_info.keys()))
        else:
            self.assertEqual(loss.loss(nut_info),
                             penalty * (nut_info[key] - limit))
            for key1 in nut_info:
                if key1 == key:
                    self.assertEqual(grad[key1], penalty)
                else:
                    self.assertEqual(grad[key1], 0)

    @given(data=infer, limit=infer, penalty=sty.from_or_0(1e-5))
    def test_target_min_limit(self, data: Tuple[NutrientInfo, Nutrient],
                              limit: float, penalty: float):
        nut_info, key = data
        loss = Target.min_limit(key, limit, penalty)
        grad = loss.gradient(nut_info)
        if nut_info[key] >= limit:
            self.assertEqual(loss.loss(nut_info), 0)
            self.assertEqual(grad, Gradient(nut_info.keys()))
        else:
            self.assertEqual(loss.loss(nut_info),
                             penalty * (limit - nut_info[key]))
            for key1 in nut_info:
                if key1 == key:
                    self.assertEqual(grad[key1], -penalty)
                else:
                    self.assertEqual(grad[key1], 0)

    @settings(deadline=500)
    @given(data=sty.collections_with_elements(2, sty.nut_infos()),
           multiplier=sty.from_or_0(1e-5),
           low_penalty=sty.from_or_0(1e-5),
           high_penalty=sty.from_or_0(1e-5))
    def test_target_relative(
            self, data: Tuple[NutrientInfo, Tuple[Nutrient, Nutrient]],
            multiplier: float, low_penalty: float, high_penalty):
        nut_info, (key0, key1) = data
        target = multiplier * nut_info[key1]
        assume(math.isfinite(target))
        loss0 = Target.relative(
            key0, key1, multiplier, low_penalty, high_penalty)
        loss1 = Target(key0, target, low_penalty, high_penalty)
        self.assertAlmostEqual(loss0.loss(nut_info), loss1.loss(nut_info))
        grad0 = loss0.gradient(nut_info)
        grad1 = loss1.gradient(nut_info)
        for key in nut_info:
            if key != key1:
                self.assertAlmostEqual(grad0[key], grad1[key])
        self.assertAlmostEqual(grad0[key1], -multiplier*grad1[key0])

    @given(key0=infer, key1=infer,
           multiplier=sty.from_or_0(1e-5), penalty=sty.from_or_0(1e-5))
    def test_target_relative_symmetric(
            self, key0: Nutrient, key1: Nutrient,
            multiplier: float, penalty: float):
        self.assertEqual(
            Target.relative(key0, key1, multiplier, penalty, penalty),
            Target.relative_symmetric(key0, key1, multiplier, penalty))

    @given(data=sty.collections_with_elements(2, sty.nut_infos()),
           multiplier=sty.reals(min_value=1e-5), penalty=sty.from_or_0(1e-5),
           nut_info=infer)
    def test_target_relative_max_limit(
            self, data: Tuple[NutrientInfo, Tuple[Nutrient, Nutrient]],
            multiplier: float, penalty: float, nut_info: NutrientInfo):
        nut_info, (key0, key1) = data
        loss = Target.relative_max_limit(key0, key1, multiplier, penalty)
        grad = loss.gradient(nut_info)
        if nut_info[key0] <= nut_info[key1] * multiplier:
            self.assertEqual(loss.loss(nut_info), 0)
            self.assertEqual(grad, NutrientInfo(nut_info.keys()))
        else:
            self.assertAlmostEqual(
                loss.loss(nut_info),
                penalty * (nut_info[key0] - multiplier*nut_info[key1]))
            for key in nut_info:
                if key == key0:
                    self.assertAlmostEqual(grad[key], penalty)
                elif key == key1:
                    self.assertAlmostEqual(grad[key], -multiplier * penalty)
                else:
                    self.assertEqual(grad[key], 0)

    @given(expr=infer, subs_key=infer, subs_expr=infer)
    def test_subs(self, expr: Expr, subs_key: Symbol, subs_expr: Expr):
        self.assertEqual(AlgebraicLoss(expr).subs(subs_key, subs_expr),
                         AlgebraicLoss(expr.subs(subs_key, subs_expr)))

    @given(key=st.sampled_from(CALORIC_VALUE))
    def test_max_energy_fraction(
            self, key: Symbol, nut_info: NutrientInfo,
            fraction: float, penalty: float):
        loss = Target.max_energy_fraction(key)
