from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa


class Categories():
    def __init__(self, vModel):
        self.vModel = vModel
        self.main_list = [
            "<Default Category>",
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
