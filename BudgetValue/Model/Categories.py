from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
from enum import Enum
import enum
import pickle
import os


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class CategoryType(AutoName):
    default_type = enum.auto()
    extra = enum.auto()
    always = enum.auto()
    reservoir = enum.auto()
    once = enum.auto()
    excess = enum.auto()

    def IsSpendable(self):
        return self in [self.always, self.reservoir, self.once]


class Category():
    def __init__(self, name, type_=None, bFavorite=False):
        assert isinstance(name, str)
        if type_ is None:
            type_ = CategoryType.default_type
        assert isinstance(type_, CategoryType)
        self.name = name
        self.type = type_
        self.bFavorite = bFavorite

    def IsSpendable(self):
        return self.type.IsSpendable()

    def GetSavable(self):
        return {'name': self.name,
                'type': self.type_,
                'bFavorite': self.bFavorite,
                }

    def LoadSavable(self, vSavable):
        self.name = vSavable['name']
        self.type_ = vSavable['type']
        self.bFavorite = vSavable['bFavorite']


class Categories(dict):
    default_category = Category("<Default Category>", CategoryType.extra)
    rent = Category("Rent", CategoryType.always)
    commute = Category("Commute", CategoryType.always)
    savings = Category("Savings", CategoryType.excess)
    __default_catagories = [
        default_category,
        rent,
        Category("Hair", CategoryType.always),
        commute,
        Category("Christmas", CategoryType.always),
        Category("Food", CategoryType.always),
        Category("Hair", CategoryType.always),
        Category("Food-Vanity", CategoryType.always),
        Category("Emergency", CategoryType.always),
        Category("Improvements", CategoryType.always),
        Category("Activities", CategoryType.always),
        savings
    ]

    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "Categories.pickle")
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

    def Save(self):
        data = list()
        for category in self.values():
            data.append(category.GetSavable())
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for category_savable in data:
            category = Category(category_savable['name'])
            self[category_savable['name']] = category
            category.LoadSavable(category_savable)

    def AddCategory(self, name, type_=None, bFavorite=False):
        if name in self.keys():
            print("WARNING: category name:"+name+" already exists")
            return
        self[name] = Category(name, type_=type_, bFavorite=bFavorite)
