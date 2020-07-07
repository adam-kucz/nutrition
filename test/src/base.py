import unittest
from typing import Iterable, TypeVar


A = TypeVar('A')


class AdvancedTestCase(unittest.TestCase):
    def assertSameElements(
            self, iter1: Iterable[A], iter2: Iterable[A]) -> None:
        self.assertEqual(sorted(iter1), sorted(iter2))
