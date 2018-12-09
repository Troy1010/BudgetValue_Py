from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import BudgetValue as BV
import sqlite3
import os
import pathlib


class Root():
    def __init__(self):
        self.sPath = str(pathlib.Path.home()) \
            + "/Documents/BudgetValue/SpendingsHistory.db"
        TM.TryMkdir(os.path.dirname(self.sPath))
        self.connection = sqlite3.connect(self.sPath)
        self.SpendingHistory = BV.Model.SpendingHistory(self)
        self.Categories = BV.Model.Categories(self)
