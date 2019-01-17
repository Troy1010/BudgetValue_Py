import os
import TM_CommonPy as TM
import pickle
import BudgetValue as BV


class PaycheckHistory(list):

    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckHistory.pickle")
        self.Load()

    def AddColumn(self):
        self.append(list())
        self.AddEntry(-1)

    def AddEntry(self, iColumn):
        self[iColumn].append(PaycheckHistoryEntry(category=self.vModel.Categories["<Default Category>"], amount=0.00))

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
