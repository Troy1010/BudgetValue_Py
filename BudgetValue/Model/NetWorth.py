import BudgetValue as BV
import os
import pickle
import rx


class NetWorth(list):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "NetWorth.pickle")
        # Structure total stream
        self.cStreams_stream = rx.subjects.Subject()

        def pseudo_lambda(cStreams):
            if not cStreams:  # all amount streams are empty
                return rx.Observable.of(0)
            else:
                return rx.Observable.combine_latest(cStreams, lambda *args: sum(args))
        self.total_stream = rx.Observable.switch_map(
            self.cStreams_stream,
            pseudo_lambda
        ).replay(1).ref_count()
        # Load
        self.Load()
        # Begin total stream
        self.total_stream.subscribe()
        self.cStreams_stream.on_next(self.GetStreams())

    def GetStreams(self):
        cActiveStreamSources = filter(lambda x: hasattr(x, '_amount_stream'), self)
        return [x._amount_stream.distinct_until_changed() for x in cActiveStreamSources]

    def __setitem__(self, key, value):
        bStreamsChange = value._amount_stream not in self.GetStreams()
        list.__setitem__(self, key, value)
        if bStreamsChange:
            self.cStreams_stream.on_next(self.GetStreams())

    def append(self, value):
        super(NetWorth, self).append(value)
        self.cStreams_stream.on_next(self.GetStreams())

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.cStreams_stream.on_next(self.GetStreams())

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
        self._amount_stream = rx.subjects.BehaviorSubject(amount)

    @property
    def amount(self):
        return self._amount_stream.value

    @amount.setter
    def amount(self, value):
        self._amount_stream.on_next(BV.MakeValid_Money(value))
