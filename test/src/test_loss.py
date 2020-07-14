import unittest
from typing import Tuple

from hypothesis import given, infer
from sympy import sympify, Symbol  # type: ignore

from src.nutritional_info import NutrientInfo
from src.loss import AlgebraicLoss
import test.src.strategy as sty


class TestLoss(unittest.TestCase):
    @given(const=sty.reals(), nut_info=infer)
    def test_constant(self, const: float, nut_info: NutrientInfo):
        loss = AlgebraicLoss(const)
        self.assertEqual(loss.loss(nut_info), const)
        self.assertEqual(loss.gradient(nut_info),
                         NutrientInfo(nut_info.keys()))

    # pylint: disable=no-value-for-parameter
    @given(const=sty.reals(), data=sty.collection_and_element(sty.nut_infos()))
    # pylint: enable=no-value-for-parameter
    def test_linear(self, const: float, data: Tuple[NutrientInfo, Symbol]):
        nut_info, key = data
        loss = AlgebraicLoss(sympify(const) * sympify(key))
        self.assertEqual(loss.loss(nut_info), const * nut_info[key])
        grad = NutrientInfo(nut_info.keys())
        grad[key] = const
        self.assertEqual(loss.gradient(nut_info), grad)
