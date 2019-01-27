import BudgetValue as BV
import rx


class AddStreamPair():
    def __init__(self, bAdd, stream):
        self.bAdd = bAdd
        self.stream = stream


class List_TotalStream(list):
    def __init__(self):
        def __TryMerge(cStreams):
            if not cStreams:  # all streams are empty
                return rx.Observable.of(0)
            else:
                return rx.Observable.merge(cStreams)

        def __AccumulateDiffStreams(accumulator, value):
            if value.bAdd:
                accumulator[value.stream] = value.stream.distinct_until_changed().pairwise().map(lambda cOldNewPair: cOldNewPair[1]-cOldNewPair[0])
            else:
                value.stream.on_next(0)
                del accumulator[value.stream]
            return accumulator
        self.__amountStream_stream = rx.subjects.Subject()
        self.total_stream = self.__amountStream_stream.scan(  # getting AddStreamPair
            __AccumulateDiffStreams,
            dict()
        ).map(  # getting dict of amountStreams:diffStreams
            lambda cAmountToDiffStreams: list(cAmountToDiffStreams.values())
        ).switch_map(  # getting collection of difference streams
            __TryMerge
        ).scan(  # getting merged difference stream
            lambda accumulator, value: accumulator + value,
            0
        ).replay(1).ref_count()
        self.total_stream.subscribe()

    def __setitem__(self, key, value):
        if self[key] != value:
            self.__amountStream_stream.on_next(AddStreamPair(False, self[key]._amount_stream))
            self.__amountStream_stream.on_next(AddStreamPair(True, value._amount_stream))
        super().__setitem__(key, value)

    def append(self, value):
        self.__amountStream_stream.on_next(AddStreamPair(True, value._amount_stream))
        super().append(value)

    def __delitem__(self, key):
        self.__amountStream_stream.on_next(AddStreamPair(False, self[key]._amount_stream))
        super().__delitem__(key)


class BalanceEntry():
    def __init__(self, total_stream, category):
        self.total_stream = total_stream
        self._category = category
        self.amount_stream = rx.subjects.BehaviorSubject(0)  # remove later

    @property
    def amount(self):
        return BV.GetLatest(self.total_stream)

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        assert isinstance(value, BV.Model.Category)
        self._category = value
