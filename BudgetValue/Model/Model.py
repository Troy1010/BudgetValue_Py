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
        self.Categories = BV.Model.Categories()
        self.ImportTransactionHistory = BV.Model.ImportTransactionHistory(self)
        self.PaycheckPlan = BV.Model.PaycheckPlan(self)
        self.Accounts = BV.Model.Accounts(self)
        self.SplitMoneyHistory = BV.Model.SplitMoneyHistory(self)
        self.SpendHistory = BV.Model.SpendHistory(self)
        self.Budgeted = BV.Model.Budgeted(self)
        self.Balance = BV.Model.Balance(self)
