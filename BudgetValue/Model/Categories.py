from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa


class Categories(list):
    def __init__(self, vModel):
        self.vModel = vModel
        default_catagory_names = [
            "<Default Category>",
            "Rent",
            "Hair",
            "Commute",
            "Christmas",
            "Food",
            "Food-Vanity",
            "Emergency",
            "Improvements",
            "Activities",
            "Savings"
        ]
        for i, vItem in enumerate(default_catagory_names):
            self.append(Category(vItem))
        self.favorites = []

    def GetTrueCategories(self):
        return [category for category in self if "<" not in category.name]


class Category():
    def __init__(self, name):
        self.name = name
        self.bFavorite = False
