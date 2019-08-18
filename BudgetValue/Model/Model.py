from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import BudgetValue as BV
import os
import atexit
import time


class Model():
    def __init__(self):
        self.start_time = time.time()
        self.sWorkspace = os.path.expanduser("~/Documents/BudgetValue/")
        TM.TryMkdir(self.sWorkspace)
        #
        self.Categories = BV.Model.Categories(self)
        self.PaycheckPlan = BV.Model.PaycheckPlan(self)
        self.Accounts = BV.Model.Accounts(self)
        self.TransactionHistory = BV.Model.TransactionHistory(self)
        self.Budgeted = BV.Model.Budgeted(self)
        self.Balance = BV.Model.Balance(self)

    def LoadAndHookSaves(self):
        self.Categories.Load()
        atexit.register(self.Categories.Save)
        self.PaycheckPlan.Load()
        atexit.register(self.PaycheckPlan.Save)
        self.Accounts.Load()
        atexit.register(self.Accounts.Save)
        self.TransactionHistory.Load()
        atexit.register(self.TransactionHistory.Save)
