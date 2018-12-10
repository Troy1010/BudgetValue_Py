

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

        def IsEmpty(self):
            return not (self.amount or self.period)
