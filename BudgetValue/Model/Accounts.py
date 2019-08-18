import BudgetValue as BV
import os
import pickle
import rx
import TM_CommonPy as TM  # noqa
from .Misc import List_TotalStream


class Accounts(List_TotalStream):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        super().__init__()
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "Accounts.pickle")

    def Save(self):
        data = list()
        for account in list(self):
            account_storable = dict()
            account_storable['name'] = account.name
            account_storable['amount'] = account.amount
            data.append(account_storable)
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
            self.append(Account())
            for k, v in net_worth_row.items():
                setattr(self[-1], k, v)


class Account():
    def __init__(self, name=None):
        self.name = name
        self.amount_stream = rx.subjects.BehaviorSubject(0)

    @property
    def amount(self):
        return self.amount_stream.value

    @amount.setter
    def amount(self, value):
        self.amount_stream.on_next(BV.MakeValid_Money(value))
