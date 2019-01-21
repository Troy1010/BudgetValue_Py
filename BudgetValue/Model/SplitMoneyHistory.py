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

    def SetEntryAndDirectOverflow(self, iColumn, categoryName, amount):
        # Set Entry amount
        for vEntry in self[iColumn]:
            if vEntry.category.name == categoryName:
                vEntry.amount = amount
        # Determine dBalance
        dBalance = Decimal(0)
        for vEntry in self[iColumn]:
            dBalance += 0 if vEntry.amount is None else vEntry.amount
        # Adjust Entry for Default Category by that amount
        for vEntry in self[iColumn]:
            if vEntry.category.name == "<Default Category>":
                vEntry.amount = - dBalance + (0 if vEntry.amount is None else vEntry.amount)
                break
        else:
            self.AddEntry(iColumn, category=self.vModel.Categories["<Default Category>"], amount=-dBalance)

    def RemoveEntry(self, iColumn, categoryName):
        iToRemove = None
        for i, vEntry in enumerate(self[iColumn]):
            if vEntry.category.name == categoryName:
                iToRemove = i
                break
        if iToRemove is not None:
            del self[iColumn][iToRemove]

    def AddColumn(self):
        self.append(list())
        self[-1].append(BalanceEntry(self[-1], self.vModel.Categories["<Default Category>"]))

    def AddEntry(self, iColumn, category=None, amount=0):
        if category is None:
            category = self.vModel.Categories["<Default Category>"]
        self[iColumn].append(SplitMoneyHistoryEntry(category=category, amount=amount))

    def Save(self):
        data = list()
        for cColumn in list(self):
            data.append(list())
            for entry in cColumn:
                data[-1].append(dict(entry))
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
            self.append(list())
            for entry in cColumn:
                if "amount" not in entry:
                    self[-1].append(BalanceEntry(self[-1], self.vModel.Categories["<Default Category>"]))
                else:
                    self[-1].append(SplitMoneyHistoryEntry(category=entry["category"], amount=entry["amount"]))


class BalanceEntry(dict):
    def __init__(self, parent, category):
        self.parent = parent
        self.category = category

    @property
    def amount(self):
        dBalance = Decimal(0)
        for item in self.parent:
            if item is not None and "amount" in item:
                dBalance += 0 if item.amount is None else item.amount
        return dBalance

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
