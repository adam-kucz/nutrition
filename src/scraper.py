from abc import abstractmethod
from pathlib import Path
from typing import NamedTuple

# import requests

from loss import Gradient


DATADIR = Path(__file__).parent.parent / "data" / "food"

API_KEY = "ib5ChiIviuKpsWkyg3IVeGtnQkTYaAahnjB9gqem"
USDA_URL = "https://api.nal.usda.gov/fdc/v1"


class SearchOptions:
    def get_results(self) -> str:
        pass


class Criteria:
    @abstractmethod
    def make_options(self, gradient: Gradient) -> SearchOptions:
        pass


class GDFields(NamedTuple):
    speed: float = 0.1


class GradientDescent(Criteria, GDFields):
    def make_options(self, gradient: Gradient) -> SearchOptions:
        


# citation:
# U.S. Department of Agriculture, Agricultural Research Service.
# FoodData Central, 2019. fdc.nal.usda.gov.
