import os
import pickle
import BudgetValue as BV
from decimal import Decimal


class SplitMoneyHistory(list):

    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "SplitMoneyHistory.pickle")
        self.Load()

    def RemoveColumn(self, iColumn):
        del self[iColumn]

    def RemoveEntry(self, iColumn, categoryName):
        del self[iColumn][categoryName]

    def AddColumn(self):
        self.append(dict())
        self._AddBalanceEntry(-1)

    def _AddBalanceEntry(self, iColumn):
        category = self.vModel.Categories["<Default Category>"]
        self[-1][category.name] = BalanceEntry(self[-1], category)

    def AddEntry(self, iColumn, category, amount=0):
        self[iColumn][category.name] = SplitMoneyHistoryEntry(category=category, amount=amount)

    def Save(self):
        data = list()
        for cColumn in list(self):
            data.append(dict())
            for k, v in cColumn.items():
                data[-1][k] = dict(v)
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for cColumn in data:
            self.AddColumn()
            for categoryName, entry in cColumn.items():
                if "amount" in entry:
                    self.AddEntry(-1, entry["category"], amount=entry["amount"])


class BalanceEntry(dict):
    def __init__(self, parent, category):
        self.parent = parent
        self.category = category

    @property
    def amount(self):
        dBalance = Decimal(0)
        for item in self.parent.values():
            if item is not None and "amount" in item:
                dBalance += 0 if item.amount is None else item.amount
        return -dBalance

    @property
    def category(self):
        return self["category"]

    @category.setter
    def category(self, value):
        self["category"] = value


class SplitMoneyHistoryEntry(dict):
    def __init__(self, category=None, amount=None):
        self.category = category
        self.amount = amount

    @property
    def amount(self):
        return self["amount"]

    @amount.setter
    def amount(self, value):
        self["amount"] = None if not value or value == 0 else BV.MakeValid_Money(value)

    @property
    def category(self):
        return self["category"]

    @category.setter
    def category(self, value):
        self["category"] = value
