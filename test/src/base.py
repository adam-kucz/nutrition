import unittest
from itertools import product


class AdvancedTestCase(unittest.TestCase):
    def assertAll(self, f, *args) -> None:
        if not args:
            return
        for (i, value0), (j, value1) in product(enumerate(args), repeat=2):
            with self.subTest(first=i, second=j):
                f(value0, value1)

    def assertAllEqual(self, *args) -> None:
        self.assertAll(self.assertEqual, *args)
