import BudgetValue as BV
import pickle
import os
import rx
from . import Misc


class PaycheckPlan(Misc.Dict_TotalStream):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        super().__init__()
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckPlan.pickle")
        self.Load()
        self["<Default Category>"] = Misc.BalanceEntry(self)

    def __setitem__(self, key, value):
        # Keys must be a category name
        if not isinstance(key, str):
            raise TypeError("Keys of " + __class__.__name__ + " must be a " + str(str) + " object")
        elif key not in self.vModel.Categories.keys():
            raise ValueError("Keys of " + __class__.__name__ + " must be the name of a category")
        #
        super().__setitem__(key, value)

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
            category_plan_storable = dict()
            category_plan_storable['amount'] = category_plan.amount
            category_plan_storable['period'] = category_plan.period
            data[categoryName] = category_plan_storable
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
            self[categoryName] = PaycheckPlanRow()
            for k, v in categoryPlan.items():
                setattr(self[categoryName], k, v)


class PaycheckPlanRow():
    def __init__(self, amount=0, period=None):
        self.amount_stream = rx.subjects.BehaviorSubject(0)
        self.amount = amount
        self.period = period

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        self._period = BV.MakeValid_Money(value)

    @property
    def amountOverPeriod(self):
        try:
            returning = self.amount / self._period
        except (ZeroDivisionError, TypeError):  # period was None
            returning = 0
        return returning

    @amountOverPeriod.setter
    def amountOverPeriod(self, value):
        self.amount = value*self._period
