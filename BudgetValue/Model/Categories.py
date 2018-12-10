from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa


class Categories():
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
        self.main_list = []
        for i, vItem in enumerate(default_catagory_names):
            self.main_list.append(Category(vItem))
        self.favorites = []


class Category():
    def __init__(self, name):
        self.name = name
        self.bFavorite = False
