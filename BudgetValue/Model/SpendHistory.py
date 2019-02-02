import os
import pickle
import BudgetValue as BV
import rx
from . import Misc  # noqa
from .Misc import GetDiffStream
from .Categories import Categories
import time


class SpendHistory(dict):
    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "SpendHistory.pickle")
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

    def values_flat(self):
        for spend_list in self.values():
            for spend in spend_list:
                yield spend

    def AddSpend(self, timestamp, amount=None, description=None, category=None):
        if timestamp not in self:
            self[timestamp] = [SpendEntry(self)]
        else:
            self[timestamp].append(SpendEntry(self))
        self[timestamp][-1].timestamp = timestamp
        if amount is not None:
            self[timestamp][-1].amount = amount
        if description is not None:
            self[timestamp][-1].description = description
        if category is not None:
            self[timestamp][-1].category = category

    def Save(self):
        data = dict()
        for k, v in dict(self).items():
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
        for item in data:
            pass


class SpendEntry():
    def __init__(self, parent):
        self.parent = parent
        self.amount_stream = rx.subjects.BehaviorSubject(0)
        self.category_stream = rx.subjects.BehaviorSubject(Categories.default_category)
        self.timestamp_stream = rx.subjects.BehaviorSubject(time.time())
        self.description_stream = rx.subjects.BehaviorSubject("")

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
    def category(self):
        return self.category_stream.value

    @category.setter
    def category(self, value):
        if isinstance(value, str) and value in Categories:
            value = Categories[value]
        assert(isinstance(value, BV.Model.Category))
        self.category_stream.on_next(value)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money_Negative(value))
