import os
import pickle
import BudgetValue as BV
from decimal import Decimal


class PaycheckHistory(list):

    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckHistory.pickle")
        self.Load()

    def Clear(self):
        del self[:]

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

    def AddColumn(self):
        self.append(list())

    def AddEntry(self, iColumn, category=None, amount=0):
        if category is None:
            category = self.vModel.Categories["<Default Category>"]
        self[iColumn].append(PaycheckHistoryEntry(category=category, amount=amount))

    def AddPaycheckPlanColumn(self):
        self.AddColumn()
        for vCategoryPlan in self.vModel.PaycheckPlan.values():
            self.AddEntry(-1, category=vCategoryPlan.category, amount=vCategoryPlan.amount)

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
                self[-1].append(PaycheckHistoryEntry(category=entry["category"], amount=entry["amount"]))


class PaycheckHistoryEntry(dict):
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
