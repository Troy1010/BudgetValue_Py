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

    def IsSpendable(self):
        return self in [self.always, self.reservoir, self.once]


class Categories(dict):
    def __init__(self, vModel):
        self.vModel = vModel
        default_catagories = [
            Category("<Default Category>", CategoryType.extra),
            Category("Paycheck", CategoryType.income),
            Category("Bonus", CategoryType.income),
            Category("Net Worth", CategoryType.income),
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

    def Select(self, types=None, types_exclude=None):
        returning = self.values()
        if types:
            returning = [category for category in returning if category.type in types]
        if types_exclude:
            returning = [category for category in returning if category.type not in types_exclude]
        return returning


class Category():
    def __init__(self, name, type_):
        assert isinstance(name, str)
        assert isinstance(type_, CategoryType)
        self.name = name
        self.type = type_
        self.bFavorite = False

    def IsSpendable(self):
        return self.type.IsSpendable()
