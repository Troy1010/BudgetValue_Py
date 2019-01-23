import BudgetValue as BV
import os
import pickle
import rx


class NetWorth(list):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "NetWorth.pickle")
        self.netWorthUpdated = rx.subjects.BehaviorSubject(None)
        self.total_Observable = self.netWorthUpdated.select(
            lambda unit: rx.Observable.combine_latest([x.amount_stream for x in self], lambda *args: sum(args))
        ).select_many(
            lambda sums: sums
        ).replay(
            1
        ).ref_count()
        self.Load()

    def __setitem__(self, key, val):
        list.__setitem__(self, key, val)
        self.netWorthUpdated.on_next(None)

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.netWorthUpdated.on_next(None)

    def AddRow(self):
        self.append(NetWorthRow())

    def RemoveRow(self, iRow):
        del self[iRow]

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


class NetWorthRow(dict):
    def __init__(self, name=None, amount=None):
        self.name = name
        self.amount_stream = rx.subjects.BehaviorSubject(amount)
        self.amount = amount

    def __setitem__(self, key, value):
        if key == "amount":
            self.amount_stream.on_next(value)
        dict.__setitem__(self, key, value)

    @property
    def amount(self):
        return self["amount"]

    @amount.setter
    def amount(self, value):
        value = None if not value or value == 0 else BV.MakeValid_Money(value)
        self["amount"] = value
        self.amount_stream.on_next(value)

    @property
    def name(self):
        return self["name"]

    @name.setter
    def name(self, value):
        self["name"] = value
