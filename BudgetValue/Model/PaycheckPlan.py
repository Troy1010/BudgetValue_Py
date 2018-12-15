import BudgetValue as BV
import pickle
import os


class PaycheckPlan(dict):
    """inherits from dict to make pickling easier"""

    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckPlan.pickle")
        self.Load()

    def __setitem__(self, key, val):
        # Keys must be a BV.Model.Category
        if not isinstance(key, BV.Model.Category):
            raise TypeError("Keys of " + __class__.__name__ + " must be a " + str(BV.Model.Category) + " object")
        # Remove keys with identical names
        for k in [k for k in self if k.name == key.name]:
            del self[k]
        #
        dict.__setitem__(self, key, val)

    def Narrate(self):
        cReturning = ["PaycheckPlan.."]
        for k, v in self.items():
            cReturning.append("Category:" + k.name + " amount:" + str(v.amount) + " period:" + str(v.period))
        return "\n\t".join(cReturning)

    def Save(self):
        data = dict()
        for category, category_plan in dict(self).items():
            data[category.name] = dict(category_plan)
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for k, v in data.items():
            self[self.vModel.Categories[k]] = self.CategoryPlan(self.vModel.Categories[k])
            for k2, v2 in v.items():
                self[self.vModel.Categories[k]][k2] = v2

    class CategoryPlan(dict):
        """inherits from dict to make pickling easier"""

        def __init__(self, category, amount=None, period=None):
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
