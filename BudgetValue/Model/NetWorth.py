import BudgetValue as BV
import os
import pickle
import TM_CommonPy as TM


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
            for k, v in net_worth_row.items():
                self[-1][k] = v

    def AddRow(self):
        self.append(NetWorthRow())

    def RemoveRow(self, iRow):
        del self[iRow]


class NetWorthRow(dict):
    def __init__(self, name=None, amount=None):
        self.name = name
        self.amount = amount

    @property
    def amount(self):
        return self["amount"]

    @amount.setter
    def amount(self, value):
        self["amount"] = None if not value or value == 0 else BV.MakeValid_Money(value)

    @property
    def name(self):
        return self["name"]

    @name.setter
    def name(self, value):
        self["name"] = value
