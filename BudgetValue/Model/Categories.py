from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
from enum import Enum
import enum


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class CategoryType(AutoName):
    extra = enum.auto()
    income = enum.auto()
    always = enum.auto()
    reservoir = enum.auto()
    once = enum.auto()
    excess = enum.auto()


class Categories(dict):
    def __init__(self, vModel):
        self.vModel = vModel
        default_catagories = [
            Category("<Default Category>", CategoryType.extra),
            Category("Rent", CategoryType.always),
            Category("Hair", CategoryType.always),
            Category("Commute", CategoryType.always),
            Category("Christmas", CategoryType.always),
            Category("Food", CategoryType.always),
            Category("Hair", CategoryType.always),
            Category("Food-Vanity", CategoryType.always),
            Category("Emergency", CategoryType.always),
            Category("Improvements", CategoryType.always),
            Category("Activities", CategoryType.always),
            Category("Savings", CategoryType.excess)
        ]
        for category in default_catagories:
            self[category.name] = category

    def GetTrueCategories(self):
        return [category for category in self.values() if category.type != CategoryType.extra]


class Category():
    def __init__(self, name, type_):
        self.name = name
        self.type = type_
        self.bFavorite = False
