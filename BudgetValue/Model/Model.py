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
        self.PaycheckHistory = BV.Model.PaycheckHistory(self)

    def GetBudgetedAmount(self, category):
        dSpendableAmount = Decimal(0)
        # PaycheckHistory total for this category
        for paycheck_history_column in self.PaycheckHistory:
            for vPaycheckHistoryEntry in paycheck_history_column:
                if vPaycheckHistoryEntry.category.name == category.name:
                    dSpendableAmount += vPaycheckHistoryEntry.amount
        # Spent total for this category
        dSpendableAmount += self.SpendingHistory.GetTotalOfAmountsOfCategory(category)
        #
        return dSpendableAmount
