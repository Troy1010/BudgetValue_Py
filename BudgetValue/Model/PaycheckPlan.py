

class PaycheckPlan():
    def __init__(self, vModel):
        self.vModel = vModel
        self.cCategoryPlans = dict()

    def Narrate(self):
        cReturning = []
        for k, v in self.cCategoryPlans.items():
            cReturning.append("Category:" + k.name + " amount:" + v.amount + " period:" + v.period)
        return "PaycheckPlan..\n\t" + "\n\t".join(cReturning)

    class CategoryPlan():
        def __init__(self, category=None, amount=None, period=None):
            self.amount = amount
            self.period = period

        def MakeValid(self, value):
            if not value or value == 0:
                return None
            else:
                return float(value)

        def IsEmpty(self):
            return not (self.amount or self.period)

        @property
        def amount(self):
            return self._amount

        @amount.setter
        def amount(self, value):
            self._amount = self.MakeValid(value)

        @property
        def period(self):
            return self._period

        @period.setter
        def period(self, value):
            self._period = self.MakeValid(value)

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
