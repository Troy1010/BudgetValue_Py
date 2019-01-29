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
        self.append(SplitMoneyHistoryColumn(self.vModel))

    def AddEntry(self, iColumn, categoryName, amount=0):
        self[iColumn][categoryName] = SplitMoneyHistoryEntry()
        self[iColumn][categoryName].amount = amount

    def Save(self):
        data = list()
        for cColumn in list(self):
            data.append(dict())
            for categoryName, vSplitMoneyHistoryEntry in cColumn.items():
                if isinstance(vSplitMoneyHistoryEntry, Misc.BalanceEntry):
                    continue
                cSplitMoneyHistoryEntry_storable = dict()
                cSplitMoneyHistoryEntry_storable['amount'] = vSplitMoneyHistoryEntry.amount
                data[-1][categoryName] = cSplitMoneyHistoryEntry_storable
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
                if categoryName == "<Default Category>":
                    continue
                self.AddEntry(-1, categoryName)
                for k, v in entry.items():
                    setattr(self[-1][categoryName], k, v)


class SplitMoneyHistoryColumn(Misc.Dict_TotalStream):
    def __init__(self, vModel):
        super().__init__()
        self.vModel = vModel
        self["<Default Category>"] = Misc.BalanceEntry(self)


class SplitMoneyHistoryEntry():
    def __init__(self):
        self.amount_stream = rx.subjects.BehaviorSubject(0)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))
