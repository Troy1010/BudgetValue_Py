import BudgetValue as BV
import os
import pickle
import rx
import TM_CommonPy as TM  # noqa


class NetWorth(list):
    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.sSaveFile = os.path.join(self.vModel.sWorkspace, "NetWorth.pickle")
        # Structure total stream

        def GetDifference(cOldNewPair):
            returning = cOldNewPair[1]-cOldNewPair[0]
            print("GetDifference. old:"+str(cOldNewPair[0])+" new:"+str(cOldNewPair[1]) + " diff:"+str(returning))
            return returning

        def Scan_CalcTotal(accumulator, value):  # Gets cStreams
            print("Scan_CalcTotal. oldtotal:"+str(accumulator)+" diff:"+str(value)+" total:"+str(accumulator + value))
            return accumulator + value

        def pseudo_lambda3(cStreams):
            print("switch_map. cStreams:"+str(cStreams))
            if not cStreams:  # all amount streams are empty
                return rx.Observable.of(0)
            else:
                return rx.Observable.combine_latest(list(cStreams), lambda *args: args)

        def ConvertAmountStreamsToDifferenceStreams(cStreams):
            return [x.pairwise().map(GetDifference) for x in cStreams]

        def AccumulateDiffStreams(accumulator, value):
            if value.bAdd:
                accumulator[value.stream] = value.stream.pairwise().map(lambda cOldNewpair: cOldNewpair[1]-cOldNewpair[0])
            else:
                value.stream.on_next(0)
                del accumulator[value.stream]
            return accumulator

        def TryMerge(cStreams):
            if not cStreams:  # all amount streams are empty
                return rx.Observable.of(0)
            else:
                return rx.Observable.merge(cStreams)

        self.accumulateStreams_stream = rx.subjects.Subject()
        self.total_stream2 = self.accumulateStreams_stream.scan(  # getting AddStreamPair
            AccumulateDiffStreams,
            dict()
        ).map(  # getting dict of amountStreams:diffStreams
            lambda cAmountToDiffStreams: list(cAmountToDiffStreams.values())
        ).switch_map(  # getting collection of difference streams
            TryMerge
        ).scan(  # getting merged difference stream
            lambda accumulator, value: accumulator + value,
            0
        )
        self.accumulateStreams_stream.subscribe(lambda x: print("new_stream:"+str(x)))
        self.total_stream2.subscribe(lambda x: print("total_stream2:"+str(x)))
        self.s1 = rx.subjects.BehaviorSubject(0)
        self.s1.subscribe(lambda x: print("s1:"+str(x)))
        # self.accumulateStreams_stream.on_next(AddStreamPair(True, self.s1))
        # self.s1.on_next(0)
        # self.s1.on_next(4)
        # self.s1.on_next(7)
        # self.s2 = rx.subjects.BehaviorSubject(0)
        # self.s2.subscribe(lambda x: print("s2:"+str(x)))
        # self.accumulateStreams_stream.on_next(AddStreamPair(True, self.s2))
        # self.s2.on_next(0)
        # self.s2.on_next(12)
        # self.s2.on_next(10)
        # self.s1.on_next(10)
        # self.accumulateStreams_stream.on_next(AddStreamPair(False, self.s1))
        print("FIRST PART DONE")
        self.cStreams_stream = rx.subjects.Subject()

        class AddStreamPair():
            def __init__(self, bAdd, stream):
                self.bAdd = bAdd
                self.stream = stream
        self.total_stream = rx.Observable.switch_map(
            self.cStreams_stream,
            TryMerge
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
