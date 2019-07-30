import os
import pickle
import BudgetValue as BV
import rx
from . import Misc  # noqa
from .Misc import GetDiffStream
from .Categories import Categories
import time


class SpendHistory(list):
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

    def AddSpend(self, timestamp=None, amount=None, description=None, category=None):
        spend = Spend(self)
        self.append(spend)
        if timestamp is not None:
            spend.timestamp = timestamp
        if amount is not None:
            spend.amount = amount
        if description is not None:
            spend.description = description
        if category is not None:
            spend.category = category

    def RemoveSpend(self, spend):
        self.remove(spend)

    def Save(self):
        data = list()
        for spend in self:
            data.append(spend.GetSavable())
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for spend_savable in data:
            spend = Spend(self)
            self.append(spend)
            spend.Load(spend_savable)


class Spend():
    def __init__(self, parent):
        self.parent = parent
        self.amount_stream = rx.subjects.BehaviorSubject(0)
        self.category_stream = rx.subjects.BehaviorSubject(Categories.default_category)
        self.timestamp_stream = rx.subjects.BehaviorSubject(time.time())
        self.description_stream = rx.subjects.BehaviorSubject("")

    def destroy(self):
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

    def GetSavable(self):
        return {'amount': self.amount,
                'categoryName': self.category.name,
                'timestamp': self.timestamp,
                'description': self.description}

    def Load(self, vSavable):
        self.amount = vSavable['amount']
        if vSavable['categoryName'] in self.parent.vModel.Categories:
            self.category = self.parent.vModel.Categories[vSavable['categoryName']]
        else:
            print("WARNING: SpendHistory- loading an unknown categoryName:"+vSavable['categoryName'])
        self.timestamp = vSavable['timestamp']
        self.description = vSavable['description']
