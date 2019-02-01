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


class Category():
    def __init__(self, name, type_):
        assert isinstance(name, str)
        assert isinstance(type_, CategoryType)
        self.name = name
        self.type = type_
        self.bFavorite = False

    def IsSpendable(self):
        return self.type.IsSpendable()


class Categories(dict):
    default_category = Category("<Default Category>", CategoryType.extra)
    default_income = Category("<Default Income>", CategoryType.income)
    __default_catagories = [
        default_category,
        default_income,
        Category("Paycheck", CategoryType.income),
        Category("Bonus", CategoryType.income),
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

    def __init__(self):
        for category in self.__default_catagories:
            self[category.name] = category

    def Select(self, types=None, types_exclude=None):
        if types is not None and not isinstance(types, list):
            types = [types]
        if types_exclude is not None and not isinstance(types_exclude, list):
            types_exclude = [types_exclude]
        returning = self.values()
        if types:
            returning = [category for category in returning if category.type in types]
        if types_exclude:
            returning = [category for category in returning if category.type not in types_exclude]
        return returning
