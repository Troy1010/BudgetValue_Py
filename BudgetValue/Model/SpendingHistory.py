import os
import pickle
import BudgetValue as BV
import rx
from . import Misc
from .Misc import GetDiffStream


class SpendingHistory(list):
    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "SpendingHistory.pickle")
        # Determine cCategoryTotalStreams
        self.cCategoryTotalStreams = dict()
        for categoryName in self.vModel.Categories.keys():
            self.cCategoryTotalStreams[categoryName] = rx.subjects.BehaviorSubject(0)
        # Load
        self.Load()
        # subscribe cCategoryTotalStreams to ImportTransactionsTotals

        def AdjustTotal(value, categoryName):
            self.cCategoryTotalStreams[categoryName].on_next(
                self.cCategoryTotalStreams[categoryName].value+value
            )

        for categoryName, stream in self.vModel.ImportTransactionHistory.cCategoryTotalStreams.items():
            GetDiffStream(stream).subscribe(
                lambda value, categoryName=categoryName: AdjustTotal(value, categoryName)
            )

    def __delitem__(self, key):
        self[key].destroy()
        super().__delitem__(key)

    def RemoveColumn(self, iColumn):
        del self[iColumn]

    def RemoveEntry(self, iColumn, categoryName):
        del self[iColumn][categoryName]

    def AddColumn(self):
        self.append(SpendingHistoryColumn(self.vModel, self))

    def AddEntry(self, iColumn, categoryName, amount=0):
        self[iColumn][categoryName] = SpendingHistoryEntry()
        self[iColumn][categoryName].amount = amount

    def Save(self):
        data = list()
        for cColumn in list(self):
            data.append(dict())
            for categoryName, vSpendingHistoryEntry in cColumn.items():
                if isinstance(vSpendingHistoryEntry, Misc.BalanceEntry):
                    continue
                cSpendingHistoryEntry_storable = dict()
                cSpendingHistoryEntry_storable['amount'] = vSpendingHistoryEntry.amount
                data[-1][categoryName] = cSpendingHistoryEntry_storable
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
                self.AddEntry(-1, categoryName)
                for k, v in entry.items():
                    setattr(self[-1][categoryName], k, v)


class SpendingHistoryColumn(Misc.Dict_TotalStream):
    def __init__(self, vModel, parent):
        assert(isinstance(vModel, BV.Model.Model))
        assert(isinstance(parent, SpendingHistory))
        super().__init__(vModel)
        self.vModel = vModel
        self.parent = parent
        self.cDisposables = dict()

        def __SubscribeCategoryTotalStream(self, stream_info):
            assert(isinstance(stream_info, BV.Model.Misc.StreamInfo))
            if stream_info.bAdd:
                disposable = stream_info.diff_stream.subscribe(
                    lambda value: self.parent.cCategoryTotalStreams[stream_info.categoryName].on_next(
                        self.parent.cCategoryTotalStreams[stream_info.categoryName].value+value
                    )
                )
                self.cDisposables[stream_info.stream] = disposable
            else:
                try:
                    self.cDisposables[stream_info.stream].dispose()
                    del self.cDisposables[stream_info.stream]
                except KeyError:
                    pass
        # Whenever a stream is added, subscribe a category_total_stream to it
        self.cDisposables[0] = self._amountStream_stream.subscribe(
            lambda stream_info: __SubscribeCategoryTotalStream(self, stream_info)
        )

    def destroy(self):
        # trigger __delitem__ for each key
        self.clear()
        # dispose all subscriptions
        for disposable in self.cDisposables.values():
            disposable.dispose()


class SpendingHistoryEntry():
    def __init__(self):
        self.amount_stream = rx.subjects.BehaviorSubject(0)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))
