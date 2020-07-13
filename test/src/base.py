import unittest
from itertools import product


class AdvancedTestCase(unittest.TestCase):
    def assertAll(self, f, *args) -> None:
        if not args:
            return
        for value0, value1 in product(args, repeat=2):
            f(value0, value1)

    def assertAllEqual(self, *args) -> None:
        self.assertAll(self.assertEqual, *args)
