import os
import TM_CommonPy as TM


class PaycheckHistory(list):

    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckHistory.pickle")
        cColumn = []
        cCategoryAmountPair = (next(iter(self.vModel.Categories)), 1.22)
        cColumn.append(cCategoryAmountPair)
        cCategoryAmountPair = (next(iter(self.vModel.Categories)), 2.33)
        cColumn.append(cCategoryAmountPair)
        self.append(cColumn)
        # self.Load()

    def AddColumn(self):
        cColumn = []
        cCategoryAmountPair = ("Title", "Title")
        cColumn.append(cCategoryAmountPair)
        self.append(cColumn)

    def Save(self):
        pass
        # data = dict()
        # for category, category_plan in dict(self).items():
        #    data[category.name] = dict(category_plan)
        # with open(self.sSaveFile, 'wb') as f:
        #     pickle.dump(data, f)

    def Load(self):
        pass
        # if not os.path.exists(self.sSaveFile):
        #     return
        # with open(self.sSaveFile, 'rb') as f:
        #     data = pickle.load(f)
        # if not data:
        #     return
        # for k, v in data.items():
        #    self[self.vModel.Categories[k]] = self.CategoryPlan(self.vModel.Categories[k])
        #    for k2, v2 in v.items():
        #        self[self.vModel.Categories[k]][k2] = v2

    class PaycheckHistoryEntry(list):
        """inherits from list to make pickling easier"""

        def __init__(self):
            pass
