import os
import pickle
import BudgetValue as BV
import rx
from . import Misc  # noqa
from .Categories import Categories  # noqa
import time


class TransactionHistory(Misc.List_ValueStream):
    def __init__(self, vModel):
        super().__init__()
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "TransactionHistory.pickle")
        # Load
        self.Load()
        self.cDisposables = {}
        self.cCategoryTotals = {}
        # Subscribe CategoryTotals to transaction_stream
        self._merged_amountStream_stream = rx.subjects.Subject()

        def MergeAmountStreamStreams(vValueAddPair):
            if vValueAddPair.bAdd:
                self.cDisposables[vValueAddPair.value] = vValueAddPair.value.categoryAmounts._amountStream_stream.subscribe(self._merged_amountStream_stream)
            else:
                self.cDisposables[vValueAddPair.value].dispose()
                del self.cDisposables[vValueAddPair.value]
        self._value_stream.subscribe(MergeAmountStreamStreams)

        def FeedCategoryTotals(stream_info):
            if stream_info.bAdd:
                if stream_info.categoryName not in self.cCategoryTotals:
                    self.cCategoryTotals[stream_info.categoryName] = rx.subjects.BehaviorSubject(0)
                self.cDisposables[stream_info.stream] = stream_info.stream.distinct_until_changed().pairwise().map(lambda cOldNewPair: cOldNewPair[1]-cOldNewPair[0]).subscribe(
                    lambda diff:
                        self.cCategoryTotals[stream_info.categoryName].on_next(
                            self.cCategoryTotals[stream_info.categoryName].value + diff
                        )
                )
            else:
                # FIX: remove empty self.cCategoryTotals[stream_info.categoryName]
                del self.cDisposables[stream_info.stream]
        self._merged_amountStream_stream.subscribe(FeedCategoryTotals)

    def Save(self):
        data = list()
        for transaction in self:
            pass
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for transaction in data:
            pass


class Transaction():
    def __init__(self, vModel, parent):
        self.parent = parent
        self.vModel = vModel
        # non-derivative data
        self.amount_stream = rx.subjects.BehaviorSubject(0)
        self.timestamp_stream = rx.subjects.BehaviorSubject(time.time())
        self.description_stream = rx.subjects.BehaviorSubject("")
        self.categoryAmounts = CategoryAmounts(vModel, parent)
        self.ValidationSource = None
        self.bAlertNonValidation = True
        # derivative data
        self.balance_stream = rx.subjects.BehaviorSubject(0)
        # subscribe balance_stream to categories total_stream
        rx.Observable.combine_latest(
            self.amount_stream,
            self.categoryAmounts.total_stream,
            lambda amount, categories_total: amount - categories_total
        ).subscribe(self.balance_stream)

    def IsOverride(self):
        return self.amount_stream.value == 0

    def IsSpend(self):
        return self.amount_stream.value < 0

    def IsIncome(self):
        return self.amount_stream.value > 0

    def destroy(self):  # FIX: is this necessary
        self.amount = 0

    @property
    def description(self):
        return self.description_stream.value

    @description.setter
    def description(self, value):
        self.description_stream.on_next(value)

    @property
    def timestamp(self):
        return self.timestamp_stream.value

    @timestamp.setter
    def timestamp(self, value):
        self.timestamp_stream.on_next(value)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))

    def GetSavable(self):
        return {'amount': self.amount,
                'timestamp': self.timestamp,
                'description': self.description}

    def Load(self, vSavable):
        self.amount = vSavable['amount']
        self.timestamp = vSavable['timestamp']
        self.description = vSavable['description']


class CategoryAmounts(Misc.Dict_TotalStream):
    def __init__(self, vModel, parent):
        super().__init__()
        self.parent = parent
        self.vModel = vModel


class CategoryAmount():
    def __init__(self, parent):
        self.parent = parent
        self.category_stream = rx.subjects.BehaviorSubject(Categories.default_category)
        self.amount_stream = rx.subjects.BehaviorSubject(0)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))

    @property
    def category(self):
        return self.category_stream.value

    @category.setter
    def category(self, value):
        if isinstance(value, str) and value in Categories:
            value = Categories[value]
        assert(isinstance(value, BV.Model.Category))
        self.category_stream.on_next(value)
