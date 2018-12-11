from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa


class Categories(dict):
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
        for i, name in enumerate(default_catagory_names):
            self[name] = Category(name)

    def GetTrueCategories(self):
        return [category for category in self.values() if "<" not in category.name]


class Category():
    def __init__(self, name):
        self.name = name
        self.bFavorite = False
