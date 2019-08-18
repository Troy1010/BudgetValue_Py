import BudgetValue as BV
import pickle
import os
import rx
from . import DataTypes
from .Categories import Categories


class PaycheckPlan(DataTypes.Dict_TotalStream):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        super().__init__()
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckPlan.pickle")

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
        for category_name, paycheck_plan_row in dict(self).items():
            if isinstance(paycheck_plan_row, DataTypes.BalanceEntry):
                continue
            category_plan_storable = dict()
            category_plan_storable['amount'] = paycheck_plan_row.amount
            category_plan_storable['period'] = paycheck_plan_row.period
            data[category_name] = category_plan_storable
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for category_name, categoryPlan in data.items():
            if category_name not in self.vModel.Categories.keys():
                continue
            self[category_name] = PaycheckPlanRow()
            for k, v in categoryPlan.items():
                setattr(self[category_name], k, v)
        self[Categories.default_category.name] = DataTypes.BalanceEntry(self, self.total_stream)


class PaycheckPlanRow():
    def __init__(self):
        self.amount_stream = rx.subjects.BehaviorSubject(0)
        self.period_stream = rx.subjects.BehaviorSubject(0)
        self.amount_over_period_stream = rx.subjects.BehaviorSubject(0)
        self.bLock = False
        # Link RowValidation to streams
        # self.amount_stream.subscribe(lambda x, item_to_keep=self.amount_stream: self.MakeRowValid(item_to_keep))
        # self.period_stream.subscribe(lambda x, item_to_keep=self.period_stream: self.MakeRowValid(item_to_keep))
        # self.amount_over_period_stream.subscribe(lambda x, item_to_keep=self.amount_over_period_stream: self.MakeRowValid(item_to_keep))

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))

    @property
    def period(self):
        return self.period_stream.value

    @period.setter
    def period(self, value):
        self.period_stream.on_next(value)  # fix: should make valid

    @property
    def amountOverPeriod(self):
        return self.amount_over_period_stream.value

    @amountOverPeriod.setter
    def amountOverPeriod(self, value):
        self.amount_over_period_stream.on_next(BV.MakeValid_Money(value))

    def MakeRowValid(self, item_to_keep):
        if not self.bLock:
            self.bLock = True
            if item_to_keep != self.amount_stream and self.amountOverPeriod and self.period:
                self.amount = self.amountOverPeriod / self.period
            elif item_to_keep != self.period_stream and self.amountOverPeriod and self.amount:
                self.period = self.amountOverPeriod / self.amount
            elif item_to_keep != self.amount_over_period_stream and self.period and self.amount:
                self.amountOverPeriod = self.amount * self.period
            self.bLock = False
