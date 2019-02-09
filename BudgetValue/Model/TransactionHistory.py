import os
import pickle
import BudgetValue as BV
import rx
from . import Misc  # noqa
from .Categories import Categories  # noqa
import time
import TM_CommonPy as TM  # noqa
import pandas as pd
from BudgetValue._Logger import Log  # noqa
import time  # noqa


class TransactionHistory(Misc.List_ValueStream):
    def __init__(self, vModel):
        super().__init__()
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "TransactionHistory.pickle")
        # subscribe _merged_amountStream_stream
        self.cDisposables = {}
        self._merged_amountStream_stream = rx.subjects.Subject()

        def MergeAmountStreamStreams(vValueAddPair):
            if vValueAddPair.bAdd:
                self.cDisposables[vValueAddPair.value] = vValueAddPair.value.categoryAmounts._amountStream_stream.subscribe(self._merged_amountStream_stream)
            else:
                self.cDisposables[vValueAddPair.value].dispose()
                del self.cDisposables[vValueAddPair.value]
        self._value_stream.subscribe(MergeAmountStreamStreams)

    def Import(self, sFilePath):
        extension = os.path.splitext(sFilePath)[1][1:]
        assert extension == 'csv'
        for index, row in pd.read_csv(sFilePath).iterrows():
            if not pd.isnull(row[3]):
                amount = row[3]
                bSpend = True
            else:
                amount = row[4]
                bSpend = False
            self.AddTransaction(bSpend, amount, timestamp=BV.ValidateTimestamp(time.time()), description=row[5])

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

    def AddTransaction(self, bSpend, amount=None, timestamp=None, description=None):
        transaction = Transaction(self.vModel, self, bSpend)
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
            transaction = Transaction(self.vModel, self, False)
            self.append(transaction)
            transaction.LoadSavable(transaction_savable)


class Transaction():
    def __init__(self, vModel, parent, bSpend):
        self.parent = parent
        self.vModel = vModel
        # non-derivative data
        self.amount_stream = rx.subjects.BehaviorSubject(0)
        self.timestamp_stream = rx.subjects.BehaviorSubject(time.time())
        self.description_stream = rx.subjects.BehaviorSubject("")
        self.categoryAmounts = CategoryAmounts(vModel, self)
        self.bSpend = bSpend
        self.ValidationSource = None  # FIX: use
        self.bAlertNonValidation = True  # FIX: use

    def SetOneCategory(self, category):
        self.categoryAmounts.clear()
        self.categoryAmounts.AddCategory(category, amount=self.amount)

    def AddCategory(self, category, amount=None):
        self.categoryAmounts.AddCategory(category, amount=amount)

    def GetCategorySummary(self):
        if len(self.categoryAmounts) == 0:
            return Categories.default_category.name
        elif len(self.categoryAmounts) == 1:
            return list(self.categoryAmounts.values())[0].category.name
        else:
            return "<Multiple Categories>"

    def IsOverride(self):
        return not self.bSpend

    def IsSpend(self):
        return self.bSpend

    def IsIncome(self):
        return not self.bSpend

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
                'categoryAmounts': {categoryName: y.amount for (categoryName, y) in self.categoryAmounts.items()},
                'bSpend': self.bSpend
                }

    def LoadSavable(self, vSavable):
        self.amount = vSavable['amount']
        self.timestamp = vSavable['timestamp']
        self.description = vSavable['description']
        if 'bSpend' in vSavable:
            self.bSpend = vSavable['bSpend']
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
        if category == Categories.default_category:
            return
        self[category.name] = CategoryAmount(self)
        self[category.name].category = category
        if amount is not None:
            self[category.name].amount = amount

    def RemoveCategory(self, category):
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
        assert isinstance(value, BV.Model.Category)
        self.category_stream.on_next(value)
