import unittest

from hypothesis import given, infer, assume, reproduce_failure

from src.nutritional_info import NutrientInfo
from src.loss import AlgebraicLoss


@unittest.skip("Unimplemented")
class TestLoss(unittest.TestCase):
    @given(const=infer, nut_info=infer)
    def test_constant(self, const: float, nut_info: NutrientInfo):
        loss = AlgebraicLoss(lambda _: const)
        self.assertEqual(loss.loss(nut_info), const)
        self.assertEqual(loss.gradient(nut_info),
                         NutrientInfo(nut_info.keys()))
