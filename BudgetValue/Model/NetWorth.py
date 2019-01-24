import BudgetValue as BV
import os
import pickle
import rx


def GetTotalStream(cStreams):
    if not cStreams:  # all streams are empty
        return rx.Observable.of(0)
    else:
        cDistinctUntilChangedStreams = list(map(lambda x: x.distinct_until_changed(), cStreams))
        return rx.Observable.combine_latest(cDistinctUntilChangedStreams, lambda *args: sum(args))


class NetWorth(list):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "NetWorth.pickle")
        # Structure total stream
        self.cStreams_stream = rx.subjects.Subject()
        self.total_Observable = rx.Observable.switch_map(
            self.cStreams_stream,
            GetTotalStream
        ).replay(1).ref_count()
        # Load
        self.Load()
        # Begin total stream
        self.total_Observable.subscribe()
        self.cStreams_stream.on_next(self.GetStreams())

    def GetStreams(self):
        return [x._amount_stream for x in filter(lambda x: hasattr(x, '_amount_stream'), self)]

    def __setitem__(self, key, value):
        bStreamsChange = value._amount_stream not in self.GetStreams()
        list.__setitem__(self, key, value)
        if bStreamsChange:
            print("cStreams_stream emission")
            self.cStreams_stream.on_next(self.GetStreams())

    def append(self, value):
        super(NetWorth, self).append(value)
        print("cStreams_stream emission")
        self.cStreams_stream.on_next(self.GetStreams())

    def __delitem__(self, key):
        list.__delitem__(self, key)
        print("cStreams_stream emission")
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
        print("Load`Close")


class NetWorthRow():
    def __init__(self, name=None, amount=0):
        self.name = name
        print("_amount_stream emission (init)")
        self._amount_stream = rx.subjects.BehaviorSubject(amount)

    @property
    def amount(self):
        return self._amount_stream.value

    @amount.setter
    def amount(self, value):
        print("_amount_stream emission (set)")
        self._amount_stream.on_next(BV.MakeValid_Money(value))
