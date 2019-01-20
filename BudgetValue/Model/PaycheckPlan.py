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

    def __setitem__(self, key, val):
        # Keys must be a BV.Model.Category
        if not isinstance(key, BV.Model.Category):
            raise TypeError("Keys of " + __class__.__name__ + " must be a " + str(BV.Model.Category) + " object")
        # Remove keys with identical names
        for k in [k for k in self if k.name == key.name]:
            del self[k]
        #
        dict.__setitem__(self, key, val)

    def DistributeBalance(self):
        default_category = self.vModel.Categories["<Default Category>"]
        # Determine dBalance
        dBalance = Decimal(0)
        for category_plan in self.values():
            if category_plan.category.name == default_category.name:
                continue
            dBalance += category_plan.amount
        # Adjust Default Category by that amount
        #  if Default Category is not in PaycheckPlan, add it
        if default_category not in self:
            self[default_category] = BV.Model.PaycheckPlan.CategoryPlan(default_category)
        #
        self[default_category].amount = -dBalance

    def SetEntryAndDirectOverflow(self, iColumn, categoryName, amount):
        """Legacy example"""
        # Set Entry amount
        for vEntry in self[iColumn]:
            if vEntry.category.name == categoryName:
                vEntry.amount = amount
        # Determine dBalance
        dBalance = Decimal(0)
        for vEntry in self[iColumn]:
            dBalance += 0 if vEntry.amount is None else vEntry.amount
        # Adjust Entry for Default Category by that amount
        for vEntry in self[iColumn]:
            if vEntry.category.name == "<Default Category>":
                vEntry.amount = - dBalance + (0 if vEntry.amount is None else vEntry.amount)
                break
        else:
            self.AddEntry(iColumn, category=self.vModel.Categories["<Default Category>"], amount=-dBalance)

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
