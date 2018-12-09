from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa


class Catagories():
    def __init__(self, vModel):
        self.vModel = vModel
        self.main_list = [
            "<Default Catagory>",
            "Rent",
            "Hair",
            "Commute",
            "Christmas",
            "Food",
            "Food-Vanity",
            "Emergency",
            "Improvements",
            "Activities"
        ]
        self.favorites = []
