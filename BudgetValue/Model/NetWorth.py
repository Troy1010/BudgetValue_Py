import BudgetValue as BV
import os
import pickle
import rx
import TM_CommonPy as TM  # noqa
from .Misc import List_TotalStream


class NetWorth(List_TotalStream):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        super().__init__()
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "NetWorth.pickle")
        # Load
        self.Load()

    def AddRow(self):
        self.append(NetWorthRow())

    def RemoveRow(self, iRow):
        del self[iRow]

    def Save(self):
        data = list()
        for net_worth_row in list(self):
            net_worth_row_storable = dict()
            net_worth_row_storable['name'] = net_worth_row.name
            net_worth_row_storable['amount'] = net_worth_row.amount
            data.append(net_worth_row_storable)
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
                setattr(self[-1], k, v)


class NetWorthRow():
    def __init__(self, name=None):
        self.name = name
        self.amount_stream = rx.subjects.BehaviorSubject(0)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))
