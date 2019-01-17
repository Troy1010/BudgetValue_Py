import os
import TM_CommonPy as TM
import pickle


class PaycheckHistory(list):

    def __init__(self, vModel):
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "PaycheckHistory.pickle")
        # self.Load()

    def AddColumn(self):
        cColumn = []
        cCategoryAmountPair = ("Title", "Title")
        cColumn.append(cCategoryAmountPair)
        self.append(cColumn)

    def AddEntry(self, iColumn):
        cCategoryAmountPair = ("Entry", "Entry")
        self[iColumn].append(cCategoryAmountPair)

    def Save(self):
        data = list()
        for cColumn in list(self):
            data.append(cColumn)
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for cColumn in data:
            self.append(cColumn)

    class PaycheckHistoryEntry(list):
        """inherits from list to make pickling easier"""

        def __init__(self):
            pass
