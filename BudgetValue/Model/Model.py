from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import BudgetValue as BV
import sqlite3
import os
from decimal import Decimal


class Model():
    def __init__(self):
        self.sWorkspace = os.path.expanduser("~/Documents/BudgetValue/")
        TM.TryMkdir(self.sWorkspace)
        self.sSpendingHistoryFile = os.path.join(self.sWorkspace, "SpendingsHistory.db")
        self.connection = sqlite3.connect(self.sSpendingHistoryFile)
        self.connection.row_factory = sqlite3.Row
        self.Categories = BV.Model.Categories(self)
        self.SpendingHistory = BV.Model.SpendingHistory(self)
        self.PaycheckPlan = BV.Model.PaycheckPlan(self)
        self.NetWorth = BV.Model.NetWorth(self)
        self.SplitMoneyHistory = BV.Model.SplitMoneyHistory(self)

    def GetBudgetedAmount(self, category):
        dSpendableAmount = Decimal(0)
        # SplitMoneyHistory total for this category
        dSpendableAmount += self.SplitMoneyHistory.cCategoryTotalStreams[category.name].value
        # Spent total for this category
        dSpendableAmount += self.SpendingHistory.cCategoryTotalStreams[category.name].value
        #
        return dSpendableAmount
