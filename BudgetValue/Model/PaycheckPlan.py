import BudgetValue as BV
import pickle
import os
from decimal import Decimal


class PaycheckPlan(dict):
    """inherits from dict to make pickling easier"""

    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckPlan.pickle")
        self.Load()
        self["<Default Category>"] = BalanceEntry(self, self.vModel.Categories["<Default Category>"])

    def __setitem__(self, key, val):
        # Keys must be a BV.Model.Category
        if not isinstance(key, str):
            raise TypeError("Keys of " + __class__.__name__ + " must be a " + str(str) + " object")
        #
        dict.__setitem__(self, key, val)

    def Narrate(self):
        cReturning = ["PaycheckPlan.."]
        for k, v in self.items():
            cReturning.append("Category:" + k.name + " amount:" + str(v.amount) + " period:" + str(v.period))
        return "\n\t".join(cReturning)

    def Save(self):
        data = dict()
        for categoryName, category_plan in dict(self).items():
            if categoryName == "<Default Category>":
                continue
            data[categoryName] = dict(category_plan)
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for categoryName, categoryPlan in data.items():
            self[categoryName] = CategoryPlan()
            for k, v in categoryPlan.items():
                if k == "category":
                    self[categoryName][k] = self.vModel.Categories[categoryName]
                else:
                    self[categoryName][k] = v


class CategoryPlan(dict):
    """inherits from dict to make pickling easier"""

    def __init__(self, category=None, amount=None, period=None):
        if category is not None:
            self.category = category
        self.amount = amount
        self.period = period

    def IsEmpty(self):
        return not (self.amount or self.period)

    @property
    def category(self):
        return self["category"]

    @category.setter
    def category(self, value):
        assert isinstance(value, BV.Model.Category)
        self["category"] = value

    @property
    def amount(self):
        return self["amount"]

    @amount.setter
    def amount(self, value):
        self["amount"] = None if not value or value == 0 else BV.MakeValid_Money(value)

    @property
    def period(self):
        return self["period"]

    @period.setter
    def period(self, value):
        self["period"] = None if not value or value == 0 else BV.MakeValid_Money(value)

    @property
    def amountOverPeriod(self):
        try:
            returning = self.amountOverPeriod / self.period
        except (ZeroDivisionError, TypeError):  # period was None
            returning = None
        return returning

    @amountOverPeriod.setter
    def amountOverPeriod(self, value):
        self.amountOverPeriod = value*self.period


class BalanceEntry(dict):
    def __init__(self, parent, category):
        self.parent = parent
        self.category = category
        self.period = None

    @property
    def amount(self):
        dBalance = Decimal(0)
        for item in self.parent.values():
            if item is not None and "amount" in item:
                dBalance += 0 if item.amount is None else item.amount
        return -dBalance

    @property
    def category(self):
        return self["category"]

    @category.setter
    def category(self, value):
        assert isinstance(value, BV.Model.Category)
        self["category"] = value
