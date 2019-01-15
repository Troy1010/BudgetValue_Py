import BudgetValue as BV
import os
import pickle


class NetWorth(list):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "NetWorth.pickle")

    def Save(self):
        data = list()
        for net_worth_row in list(self):
            data.append(dict(net_worth_row))
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = pickle.load(f)
        if not data:
            return
        for net_worth_row in data:
            self.append(NetWorthRow())
            for k, v in net_worth_row:
                self[-1][k] = v

    def AddRow(self):
        self.append(NetWorthRow())


class NetWorthRow(dict):
    def __init__(self, name=None, amount=None):
        self["name"] = name
        self.name = name
        self["amount"] = amount
        self.amount = amount
