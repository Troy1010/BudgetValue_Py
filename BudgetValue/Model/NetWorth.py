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
        self.total_Observable = rx.Observable.switch_map(
            self.netWorthUpdated,
            lambda unit: rx.Observable.combine_latest([x.amount_stream for x in self], lambda *args: sum(args))
        ).replay(1).ref_count()
        self.Load()

    def __setitem__(self, key, val):
        bUpdate = key not in self
        list.__setitem__(self, key, val)
        if bUpdate:
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
    def __init__(self, name=None, amount=0):
        self.name = name
        self.amount_stream = rx.subjects.BehaviorSubject(amount)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        if value and value != self.amount_stream.value:
            self.amount_stream.on_next(BV.MakeValid_Money(value))
