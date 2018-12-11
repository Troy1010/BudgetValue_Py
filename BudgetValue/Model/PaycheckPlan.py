import BudgetValue as BV
import pickle
import os


class PaycheckPlan(dict):

    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckPlan.pickle")

    def __setitem__(self, key, val):
        # Keys must be a BV.Model.Category
        if not isinstance(key, BV.Model.Category):
            raise TypeError("Keys of " + __class__.__name__ + " must be a "+str(BV.Model.Category)+" object")
        # Remove a key with an identical name
        vDeleteMe = None
        for k in self:
            if k.name == key.name:
                vDeleteMe = k
                break
        if vDeleteMe:
            del self[vDeleteMe]
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
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        for k, v in data.items():
            self[self.vModel.Categories[k]] = self.CategoryPlan()
            for k2, v2 in v.items():
                self[self.vModel.Categories[k]][k2] = v2

    class CategoryPlan(dict):

        def __init__(self, amount=None, period=None):
            self.amount = amount
            self.period = period

        def ValidationHandler(self, value):
            if not value or value == 0:
                return None
            else:
                return BV.MakeValid_Money(value)

        def IsEmpty(self):
            return not (self.amount or self.period)

        @property
        def amount(self):
            return self["amount"]

        @amount.setter
        def amount(self, value):
            self["amount"] = self.ValidationHandler(value)

        @property
        def period(self):
            return self["period"]

        @period.setter
        def period(self, value):
            self["period"] = self.ValidationHandler(value)

        @property
        def amountPerWeek(self):
            try:
                returning = self.amount / self.period
            except (ZeroDivisionError, TypeError):  # period was None
                returning = None
            return returning

        @amountPerWeek.setter
        def amountPerWeek(self, value):
            self.amount = value*self.period
