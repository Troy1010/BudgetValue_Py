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
        #
        self.cCategoryTotals = {}
        self.total_stream = rx.subjects.BehaviorSubject(0)
        # Subscribe CategoryTotals
        self.cDisposables = {}
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
                self.cDisposables[stream_info.stream].dispose()
                del self.cDisposables[stream_info.stream]
        self._merged_amountStream_stream.subscribe(FeedCategoryTotals)
        # Subscribe total_stream
        self.cDisposables2 = {}

        def FeedTotal(stream_info):
            if stream_info.bAdd:
                self.cDisposables2[stream_info.categoryName] = stream_info.stream.distinct_until_changed().pairwise().map(lambda cOldNewPair: cOldNewPair[1]-cOldNewPair[0]).subscribe(
                    lambda diff:
                        self.total_stream.on_next(
                            self.total_stream.value + diff
                        )
                )
            else:
                self.cDisposables2[stream_info.categoryName].dispose()
                del self.cDisposables2[stream_info.categoryName]
        self._merged_amountStream_stream.subscribe(FeedTotal)
        # Load
        self.Load()

    def Iter_Spend(self):
        for transaction in self:
            if transaction.IsSpend():
                yield transaction

    def Iter_Income(self):
        for transaction in self:
            if transaction.IsIncome() or transaction.IsOverride():
                yield transaction

    def GetIncome(self):
        return list(self.Iter_Income())

    def GetSpends(self):
        return list(self.Iter_Spend())

    def AddTransaction(self, amount=None, timestamp=None, description=None):
        transaction = Transaction(self.vModel, self)
        self.append(transaction)
        if amount is not None:
            transaction.amount = amount
        if timestamp is not None:
            transaction.timestamp = timestamp
        if description is not None:
            transaction.description = description
        return transaction

    def RemoveTransaction(self, transaction):
        if isinstance(transaction, Transaction):
            self.remove(transaction)
        elif isinstance(transaction, int):
            del self[transaction]

    def Save(self):
        data = list()
        for transaction in self:
            data.append(transaction.GetSavable())
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for transaction_savable in data:
            transaction = Transaction(self.vModel, self)
            self.append(transaction)
            transaction.LoadSavable(transaction_savable)


class Transaction():
    def __init__(self, vModel, parent):
        self.parent = parent
        self.vModel = vModel
        # non-derivative data
        self.amount_stream = rx.subjects.BehaviorSubject(0)
        self.timestamp_stream = rx.subjects.BehaviorSubject(time.time())
        self.description_stream = rx.subjects.BehaviorSubject("")
        self.categoryAmounts = CategoryAmounts(vModel, self)
        self.ValidationSource = None  # FIX: use
        self.bAlertNonValidation = True  # FIX: use

    def IsOverride(self):
        return self.amount_stream.value == 0

    def IsSpend(self):
        return self.amount_stream.value < 0

    def IsIncome(self):
        return self.amount_stream.value > 0

    def destroy(self):
        self.categoryAmounts.clear()
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
                'description': self.description,
                'categoryAmounts': {categoryName: y.amount for (categoryName, y) in self.categoryAmounts.items()}
                }

    def LoadSavable(self, vSavable):
        self.amount = vSavable['amount']
        self.timestamp = vSavable['timestamp']
        self.description = vSavable['description']
        for categoryName, amount in vSavable['categoryAmounts'].items():
            self.categoryAmounts.AddCategory(self.vModel.Categories[categoryName], amount)


class CategoryAmounts(Misc.Dict_TotalStream):
    def __init__(self, vModel, parent):
        super().__init__()
        self.parent = parent
        self.vModel = vModel
        # derivative data
        self.balance_stream = rx.subjects.BehaviorSubject(0)
        # manually merge balance_stream into parent's cCategoryTotals
        self.parent.parent._merged_amountStream_stream.on_next(Misc.StreamInfo(True, self.balance_stream, Categories.default_category.name))
        # subscribe balance_stream
        rx.Observable.combine_latest(
            self.parent.amount_stream,
            self.total_stream,
            lambda amount, categories_total: amount - categories_total
        ).subscribe(self.balance_stream)

    def GetAll(self):
        cAll = dict(self)
        default_category_amount = CategoryAmount(self)
        default_category_amount.category = Categories.default_category
        default_category_amount.amount_stream = self.balance_stream
        cAll[Categories.default_category.name] = default_category_amount
        return cAll

    def AddCategory(self, category, amount=None):
        assert(category != Categories.default_category)
        self[category.name] = CategoryAmount(self)
        self[category.name].category = category
        if amount is not None:
            self[category.name].amount = amount

    def RemoveCategory(self, category, amount=None):
        assert(category != Categories.default_category)
        del self[category.name]


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
