from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import BudgetValue as BV
import sqlite3
import os


class Model():
    def __init__(self):
        self.sWorkspace = os.path.expanduser("~/Documents/BudgetValue/")
        TM.TryMkdir(self.sWorkspace)
        self.sSpendingHistoryFile = os.path.join(self.sWorkspace, "SpendingsHistory.db")
        self.connection = sqlite3.connect(self.sSpendingHistoryFile)
        self.connection.row_factory = sqlite3.Row
        self.SpendingHistory = BV.Model.SpendingHistory(self)
        self.Categories = BV.Model.Categories(self)
        self.PaycheckPlan = BV.Model.PaycheckPlan(self)
