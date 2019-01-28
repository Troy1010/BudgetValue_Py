import BudgetValue as BV
import rx
import TM_CommonPy as TM  # noqa


class AddStreamPair():
    def __init__(self, bAdd, stream):
        self.bAdd = bAdd
        self.stream = stream


class Dict_AmountStreamStream(dict):
    def __init__(self):
        super().__init__()
        self._amountStream_stream = rx.subjects.Subject()

    def __setitem__(self, key, value):
        # if we have an old value and it isn't the new value, remove old value
        if key in self and hasattr(self[key], '_amount_stream') and self[key] != value:
            self._amountStream_stream.on_next(AddStreamPair(False, self[key]._amount_stream))
        # if new value isn't the old value, add that new value
        if hasattr(value, '_amount_stream') and (key not in self or self[key] != value):
            self._amountStream_stream.on_next(AddStreamPair(True, value._amount_stream))
        super().__setitem__(key, value)

    def __delitem__(self, key):
        if key in self and hasattr(self[key], '_amount_stream'):
            self._amountStream_stream.on_next(AddStreamPair(False, self[key]._amount_stream))
        super().__delitem__(key)


class List_AmountStreamStream(list):
    def __init__(self):
        super().__init__()
        self._amountStream_stream = rx.subjects.Subject()

    def __setitem__(self, key, value):
        # if value has _amount_stream and value isn't old, remove the old and add the new
        if key in self and self[key] != value:
            if hasattr(self[key], '_amount_stream'):
                self._amountStream_stream.on_next(AddStreamPair(False, self[key]._amount_stream))
            if hasattr(value, '_amount_stream'):
                self._amountStream_stream.on_next(AddStreamPair(True, value._amount_stream))
        super().__setitem__(key, value)

    def append(self, value):
        if hasattr(value, '_amount_stream'):
            self._amountStream_stream.on_next(AddStreamPair(True, value._amount_stream))
        super().append(value)

    def __delitem__(self, key):
        if key in self and hasattr(self[key], '_amount_stream'):
            self._amountStream_stream.on_next(AddStreamPair(False, self[key]._amount_stream))
        super().__delitem__(key)


class TotalStream_Inheritable():
    def __init__(self):
        super().__init__()

        def __TryMerge(cStreams):
            if not cStreams:  # all streams are empty
                return rx.Observable.of(0)
            else:
                return rx.Observable.merge(cStreams)

        def __AccumulateDiffStreams(accumulator, value):
            assert(isinstance(value, AddStreamPair))
            if value.bAdd:
                accumulator[value.stream] = value.stream.distinct_until_changed().pairwise().map(lambda cOldNewPair: cOldNewPair[1]-cOldNewPair[0])
            else:
                value.stream.on_next(0)
                del accumulator[value.stream]
            return accumulator
        self.total_stream = rx.subjects.BehaviorSubject(0)  # can probably make it a regular stream when there is no Refresh()
        self._amountStream_stream.filter(  # filter out BalanceEntry
            lambda cAddStreamPair: cAddStreamPair.stream != self.total_stream
        ).scan(  # getting AddStreamPair
            __AccumulateDiffStreams,
            dict()
        ).map(  # getting dict of amountStreams:diffStreams
            lambda cAmountToDiffStreams: list(cAmountToDiffStreams.values())
        ).switch_map(  # getting collection of difference streams
            __TryMerge
        ).scan(  # getting merged difference stream
            lambda accumulator, value: BV.MakeValid_Money(accumulator + value),
            0
        ).publish().ref_count().subscribe(self.total_stream)
        self.total_stream.subscribe()
        self.total = 0

        def SetTotal(self, total):
            self.total = total
        self.total_stream.subscribe(lambda total: SetTotal(self, total))


class List_TotalStream(TotalStream_Inheritable, List_AmountStreamStream):
    pass


class Dict_TotalStream(TotalStream_Inheritable, Dict_AmountStreamStream):
    pass


class BalanceEntry():
    def __init__(self, parent):
        self.parent = parent
        self._category = self.parent.vModel.Categories["<Default Category>"]
        self._amount_stream = self.parent.total_stream

    @property
    def amount(self):
        return -self.parent.total

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        assert isinstance(value, BV.Model.Category)
        self._category = value
