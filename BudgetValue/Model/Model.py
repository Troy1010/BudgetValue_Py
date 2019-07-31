from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import BudgetValue as BV
import os


class Model():
    def __init__(self):
        self.sWorkspace = os.path.expanduser("~/Documents/BudgetValue/")
        TM.TryMkdir(self.sWorkspace)
        #
        self.Categories = BV.Model.Categories(self)
        self.PaycheckPlan = BV.Model.PaycheckPlan(self)
        self.Accounts = BV.Model.Accounts(self)
        self.TransactionHistory = BV.Model.TransactionHistory(self)
        self.Budgeted = BV.Model.Budgeted(self)
        self.Balance = BV.Model.Balance(self)
        # Load
        self.TransactionHistory.Load()
