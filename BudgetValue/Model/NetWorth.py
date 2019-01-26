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
            if not cStreams:  # all amount streams are empty
                return rx.Observable.of(0)
            else:
                return rx.Observable.merge(cStreams)

        def AccumulateDiffStreams(accumulator, value):
            if value is None:
                return accumulator
            if value.bAdd:
                accumulator[value.stream] = value.stream.pairwise().map(lambda cOldNewpair: cOldNewpair[1]-cOldNewpair[0])
            else:
                value.stream.on_next(0)
                del accumulator[value.stream]
            return accumulator

        def Scan_CalcTotal(accumulator, value):
            print("Scan_CalcTotal. oldtotal:"+str(accumulator)+" diff:"+str(value)+" total:"+str(accumulator + value))
            return accumulator + value

        self.stream_stream = rx.subjects.Subject()
        self.total_stream = self.stream_stream.scan(  # getting AddStreamPair
            AccumulateDiffStreams,
            dict()
        ).map(  # getting dict of amountStreams:diffStreams
            lambda cAmountToDiffStreams: list(cAmountToDiffStreams.values())
        ).switch_map(  # getting collection of difference streams
            TryMerge
        ).scan(  # getting merged difference stream
            Scan_CalcTotal,
            0
        )
        # Load
        self.Load()
        #
        self.total_stream.subscribe(lambda x: print("total_stream:"+str(x)))
        self.stream_stream.subscribe(lambda x: print("stream_stream:"+str(x)))
        # Begin total stream
        self.total_stream.subscribe()
        self.stream_stream.on_next(None)

    def __setitem__(self, key, value):
        raise Exception("Set item")
        bStreamsChange = value._amount_stream not in self.GetStreams()
        list.__setitem__(self, key, value)
        if bStreamsChange:
            self.stream_stream.on_next(self.GetStreams())

    def append(self, value):
        super(NetWorth, self).append(value)
        self.stream_stream.on_next(AddStreamPair(True, value.amount))

    def __delitem__(self, key):
        value = self[key]
        list.__delitem__(self, key)
        self.stream_stream.on_next(AddStreamPair(False, value.amount))

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
