from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import BudgetValue as BV
import sqlite3
import os
import pathlib

from .SpendingHistory import SpendingHistory
from .Catagories import Catagories


class Model():
    SpendingHistory = SpendingHistory
    Catagories = Catagories

    def __init__(self):
        self.sPath = str(pathlib.Path.home()) \
            + "/Documents/BudgetValue/SpendingsHistory.db"
        TM.TryMkdir(os.path.dirname(self.sPath))
        self.connection = sqlite3.connect(self.sPath)
        self.SpendingHistory = BV.Model.SpendingHistory(self)
        self.Catagories = BV.Model.Catagories(self)
