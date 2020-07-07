from collections import UserList
from typing import Iterable, Collection, Mapping

from .nutritional_info import NutrientInfo, VOID_NUTRIENT
from .loss import Loss


class Food(NutrientInfo):
    def __init__(
            self, name: str, data: NutrientInfo, amount: float = 0) -> None:
        super().__init__(data)
        self.__name = name
        self.amount = amount

    @property
    def name(self) -> str:
        return self.__name

    def nutrients(self) -> NutrientInfo:
        return self * self.amount


VOID_FOOD = Food("void", VOID_NUTRIENT)


class FoodPlan(UserList, Collection[Food]):
    def __init__(self, foods: Iterable[Food] = (),
                 losses: Iterable[Loss] = ()) -> None:
        super().__init__(foods)
        self.losses = list(losses)

    def total_loss(self) -> float:
        value = sum(map(Food.nutrients, self.data), VOID_NUTRIENT)
        return sum(loss.loss(value) for loss in self.losses)

    def gradient(self) -> Mapping[str, float]:
        value = sum(map(Food.nutrients, self.data), VOID_NUTRIENT)
        gradient = sum((loss.gradient(value) for loss in self.losses),
                       VOID_NUTRIENT)
        return {
            food.name: food * gradient for food in self.data}
