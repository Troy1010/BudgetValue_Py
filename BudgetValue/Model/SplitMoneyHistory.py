import os
import pickle
import BudgetValue as BV
import rx
from . import Misc


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
        self.append(SplitMoneyHistoryColumn())

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


class SplitMoneyHistoryColumn(Misc.Dict_TotalStream):
    def __init__(self):
        super().__init__()
        self["<Default Category>"] = Misc.BalanceEntry(self)


class SplitMoneyHistoryEntry():
    def __init__(self, category=None, amount=0):
        self.category = category
        self._amount_stream = rx.subjects.BehaviorSubject(0)
        self.amount = amount

    @property
    def amount(self):
        return self._amount_stream.value

    @amount.setter
    def amount(self, value):
        self._amount_stream.on_next(BV.MakeValid_Money(value))
