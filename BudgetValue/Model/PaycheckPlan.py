import BudgetValue as BV
import pickle
import os
import rx


def sum2(args):
    print("total_Observable. value:"+str(sum(args)))
    return sum(args)


class PaycheckPlan(dict):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckPlan.pickle")
        self.paycheckPlanUpdated = rx.subjects.BehaviorSubject(None)
        self.total_Observable = rx.Observable.switch_map(
            self.paycheckPlanUpdated,
            lambda unit: rx.Observable.combine_latest([x.amount_stream for x in self.values()], lambda *args: BV.MakeValid_Money(sum2(args)))
        ).replay(1).ref_count()
        self.Load()
        self["<Default Category>"] = BalanceEntry(self.total_Observable, self.vModel.Categories["<Default Category>"])

    def __setitem__(self, key, value):
        # Keys must be a category name
        if not isinstance(key, str):
            raise TypeError("Keys of " + __class__.__name__ + " must be a " + str(str) + " object")
        elif key not in self.vModel.Categories.keys():
            raise TypeError("Keys of " + __class__.__name__ + " must be the name of a category")
        #
        bUpdate = value.amount_stream not in [x.amount_stream for x in self.values()]
        dict.__setitem__(self, key, value)
        if bUpdate:
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
            self[categoryName] = CategoryPlan()
            for k, v in categoryPlan.items():
                if k == 'categoryName':
                    self[categoryName].category = self.vModel.Categories[categoryName]
                else:
                    setattr(self[categoryName], k, v)


class CategoryPlan():
    def __init__(self, category=None, amount=0, period=None):
        self._category = category
        self.amount_stream = rx.subjects.BehaviorSubject(amount)
        self._period = period

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        assert isinstance(value, BV.Model.Category) or value is None
        self._category = value

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        if BV.MakeValid_Money(value) != self.amount_stream.value:
            print("amount_stream emitting. value:"+str(value))
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


class BalanceEntry():
    def __init__(self, total_stream, category):
        self.total_stream = total_stream
        self._category = category
        self.amount_stream = rx.subjects.BehaviorSubject(0)  # remove later

    @property
    def amount(self):
        return BV.MakeValid_Money(BV.GetLatest(self.total_stream))

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        assert isinstance(value, BV.Model.Category)
        self._category = value
