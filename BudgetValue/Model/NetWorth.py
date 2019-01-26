import BudgetValue as BV
import os
import pickle
import rx
import TM_CommonPy as TM  # noqa


class AddStreamPair():
    def __init__(self, bAdd, stream):
        self.bAdd = bAdd
        self.stream = stream


class NetWorth(list):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "NetWorth.pickle")
        # Structure total stream

        def TryMerge(cStreams):
            if not cStreams:  # all streams are empty
                return rx.Observable.of(0)
            else:
                return rx.Observable.merge(cStreams)

        def AccumulateDiffStreams(accumulator, value):
            if value.bAdd:
                accumulator[value.stream] = value.stream.distinct_until_changed().pairwise().map(lambda cOldNewPair: cOldNewPair[1]-cOldNewPair[0])
            else:
                value.stream.on_next(0)
                del accumulator[value.stream]
            return accumulator

        self.amountStream_stream = rx.subjects.Subject()
        self.total_stream = self.amountStream_stream.scan(  # getting AddStreamPair
            AccumulateDiffStreams,
            dict()
        ).map(  # getting dict of amountStreams:diffStreams
            lambda cAmountToDiffStreams: list(cAmountToDiffStreams.values())
        ).switch_map(  # getting collection of difference streams
            TryMerge
        ).scan(  # getting merged difference stream
            lambda accumulator, value: accumulator + value,
            0
        ).replay(1).ref_count()
        self.total_stream.subscribe()
        # Load
        self.Load()

    def __setitem__(self, key, value):
        if self[key] != value:
            self.amountStream_stream.on_next(AddStreamPair(False, self[key]._amount_stream))
            self.amountStream_stream.on_next(AddStreamPair(True, value._amount_stream))
        super().__setitem__(key, value)

    def append(self, value):
        self.amountStream_stream.on_next(AddStreamPair(True, value._amount_stream))
        super().append(value)

    def __delitem__(self, key):
        self.amountStream_stream.on_next(AddStreamPair(False, self[key]._amount_stream))
        super().__delitem__(key)

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
        self._amount_stream = rx.subjects.BehaviorSubject(0)
        self.amount = amount

    @property
    def amount(self):
        return self._amount_stream.value

    @amount.setter
    def amount(self, value):
        self._amount_stream.on_next(BV.MakeValid_Money(value))
