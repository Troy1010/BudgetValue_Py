from BudgetValue._Logger import Log  # noqa
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
from enum import Enum
import enum
import pickle
import os
import atexit


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class CategoryType(AutoName):
    extra = enum.auto()
    always = enum.auto()
    reservoir = enum.auto()
    once = enum.auto()
    default_type = enum.auto()
    excess = enum.auto()

    def GetIndex(type_):
        for i, category_type in enumerate(CategoryType):
            if type_ == category_type:
                return i
        return -1

    def GetByName(name):
        for category_type in CategoryType:
            if category_type.name.lower() == name.lower():
                return category_type
        return None

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
        if self.type is None:
            return False
        return self.type.IsSpendable()

    def GetSavable(self):
        return {'name': self.name,
                'type': self.type,
                'bFavorite': self.bFavorite,
                }

    def LoadSavable(self, vSavable):
        self.name = vSavable['name']
        self.type = vSavable['type']
        self.bFavorite = vSavable['bFavorite']


class Categories(dict):
    default_category = Category("<Default Category>", CategoryType.extra)
    savings = Category("Savings", CategoryType.excess)
    __mandatory_catagories = [
        default_category,
        savings
    ]
    rent = Category("Rent", CategoryType.always)
    commute = Category("Commute", CategoryType.always)
    __default_catagories = [
        rent,
        Category("Hair", CategoryType.always),
        commute,
        Category("Christmas", CategoryType.always),
        Category("Food", CategoryType.always),
        Category("Hair", CategoryType.always),
        Category("Food-Vanity", CategoryType.always),
        Category("Emergency", CategoryType.always),
        Category("Improvements", CategoryType.always),
        Category("Activities", CategoryType.always)
    ]

    def __init__(self, vModel):
        self.vModel = vModel
        # Load and hook save on exit
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "Categories.pickle")
        self.Load()
        for category in self.__mandatory_catagories:
            self[category.name] = category
        atexit.register(self.Save)

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
        returning = sorted(returning, key=lambda category: CategoryType.GetIndex(category.type))  # self should be a sorted dict to avoid this..
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
            for category in self.__default_catagories:
                self[category.name] = category
            return
        for category_savable in data:
            category = Category(category_savable['name'])
            self[category_savable['name']] = category
            category.LoadSavable(category_savable)

    def AddCategory(self, name, type_=None, bFavorite=False):
        if name in self.keys():
            BVLog.warning("WARNING: categoryName:"+name+" already exists")
            return
        self[name] = Category(name, type_=type_, bFavorite=bFavorite)

    def RemoveCategory(self, name):
        if name in self.__mandatory_catagories:
            BVLog.warning("WARNING: tried to remove mandatory category name:"+name)
            return
        del self[name]

    def AssignCategoryType(self, name, type_):
        self[name].type = type_
