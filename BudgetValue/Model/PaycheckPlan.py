import BudgetValue as BV
import pickle
import os
import rx
import TM_CommonPy as TM  # noqa


class PaycheckPlan(dict):
    """inherits from dict to make pickling easier"""

    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckPlan.pickle")
        self.paycheckPlanUpdated = rx.subjects.BehaviorSubject(None)
        self.total = rx.subjects.BehaviorSubject(0)
        self.paycheckPlanUpdated.select(
            lambda unit: self.GenerateTotalObservable(unit)
        ).select_many(
            lambda sums: sums
        ).replay(
            1
        ).ref_count().subscribe(self.total)
        self.Load()
        self["<Default Category>"] = BalanceEntry(self, self.vModel.Categories["<Default Category>"])

    def GenerateTotalObservable(self, unit):
        cStreams = [x.amount_stream for x in self.values()]
        if cStreams:
            return rx.Observable.combine_latest(cStreams, lambda *args: self.CalcTotal(args))
        else:
            return rx.Observable.from_list([0])

    def CalcTotal(self, args):
        total = sum(args)
        return None if not total or total == 0 else BV.MakeValid_Money(total)

    def __setitem__(self, key, val):
        # Keys must be a BV.Model.Category
        if not isinstance(key, str):
            raise TypeError("Keys of " + __class__.__name__ + " must be a " + str(str) + " object")
        #
        bUpdated = False
        if key not in self:
            bUpdated = True
        dict.__setitem__(self, key, val)
        if bUpdated:
            self.paycheckPlanUpdated.on_next(None)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.paycheckPlanUpdated.on_next(None)

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
                elif k == "amount":
                    self[categoryName].amount = v
                else:
                    self[categoryName][k] = v


class CategoryPlan(dict):
    """inherits from dict to make pickling easier"""

    def __init__(self, category=None, amount=None, period=None):
        if category is not None:
            self.category = category
        self.amount_stream = rx.subjects.BehaviorSubject(amount)
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
        value = None if not value or value == 0 else BV.MakeValid_Money(value)
        self["amount"] = value
        value = 0 if value is None else value
        self.amount_stream.on_next(value)

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
        self.amount_stream = rx.subjects.BehaviorSubject(0)

    @property
    def amount(self):
        return None if not self.parent.total.value or self.parent.total.value == 0 else BV.MakeValid_Money(self.parent.total.value)

    @property
    def category(self):
        return self["category"]

    @category.setter
    def category(self, value):
        assert isinstance(value, BV.Model.Category)
        self["category"] = value
