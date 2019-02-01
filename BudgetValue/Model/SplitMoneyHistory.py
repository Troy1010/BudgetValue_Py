import os
import pickle
import BudgetValue as BV
import rx
from . import Misc
from .Categories import Categories


class SplitMoneyHistory(list):
    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "SplitMoneyHistory.pickle")
        # Determine cCategoryTotalStreams
        self.cCategoryTotalStreams = dict()
        for categoryName in self.vModel.Categories.keys():
            self.cCategoryTotalStreams[categoryName] = rx.subjects.BehaviorSubject(0)
        # Load
        self.Load()

    def __delitem__(self, key):
        self[key].destroy()
        super().__delitem__(key)

    def RemoveColumn(self, iColumn):
        del self[iColumn]

    def RemoveEntry(self, iColumn, categoryName):
        del self[iColumn][categoryName]

    def AddColumn(self):
        self.append(SplitMoneyHistoryColumn(self.vModel, self))

    def AddEntry(self, iColumn, categoryName, amount=0):
        if isinstance(categoryName, BV.Model.Category):
            categoryName = categoryName.name
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
                cSplitMoneyHistoryEntry_storable['bIncome'] = self.vModel.Categories[categoryName].type == BV.Model.CategoryType.income
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
                if categoryName == Categories.default_category.name:
                    continue
                if categoryName not in self.vModel.Categories.keys():
                    print("WARNING: SplitMoneyHistory- loading an unknown categoryName:"+categoryName)
                    continue
                self.AddEntry(-1, categoryName)
                for k, v in entry.items():
                    setattr(self[-1][categoryName], k, v)


class SplitMoneyHistoryColumn(Misc.Dict_TotalStream):
    def __init__(self, vModel, parent):
        assert(isinstance(vModel, BV.Model.Model))
        assert(isinstance(parent, SplitMoneyHistory))
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
        #
        self[Categories.default_category.name] = Misc.BalanceEntry(self, self.total_stream)
        __SubscribeCategoryTotalStream(self, BV.Model.Misc.StreamInfo(True, self[Categories.default_category.name].amount_stream, Categories.default_category.name))
        # FIX: The above command should be unnecessary, but BalanceEntry is currently filtered from _amount_stream

    def destroy(self):
        # trigger __delitem__ for each key
        self.clear()
        # dispose all subscriptions
        for disposable in self.cDisposables.values():
            disposable.dispose()


class SplitMoneyHistoryEntry():
    def __init__(self):
        self.amount_stream = rx.subjects.BehaviorSubject(0)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))
