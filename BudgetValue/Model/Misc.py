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
        if key in self and hasattr(self[key], 'amount_stream') and self[key] != value:
            self._amountStream_stream.on_next(AddStreamPair(False, self[key].amount_stream))
        # if new value isn't the old value and new value isn't a BalanceEntry, add that new value
        if hasattr(value, 'amount_stream') and (key not in self or self[key] != value) and not isinstance(value, BalanceEntry):
            self._amountStream_stream.on_next(AddStreamPair(True, value.amount_stream))
        super().__setitem__(key, value)

    def __delitem__(self, key):
        if key in self and hasattr(self[key], 'amount_stream'):
            self._amountStream_stream.on_next(AddStreamPair(False, self[key].amount_stream))
        super().__delitem__(key)


class List_AmountStreamStream(list):
    def __init__(self):
        super().__init__()
        self._amountStream_stream = rx.subjects.Subject()

    def __setitem__(self, key, value):
        # if value has amount_stream and value isn't old, remove the old and add the new
        if key in self and self[key] != value:
            if hasattr(self[key], 'amount_stream'):
                self._amountStream_stream.on_next(AddStreamPair(False, self[key].amount_stream))
            if hasattr(value, 'amount_stream') and not isinstance(value, BalanceEntry):
                self._amountStream_stream.on_next(AddStreamPair(True, value.amount_stream))
        super().__setitem__(key, value)

    def append(self, value):
        if hasattr(value, 'amount_stream') and not isinstance(value, BalanceEntry):
            self._amountStream_stream.on_next(AddStreamPair(True, value.amount_stream))
        super().append(value)

    def __delitem__(self, key):
        if key in self and hasattr(self[key], 'amount_stream'):
            self._amountStream_stream.on_next(AddStreamPair(False, self[key].amount_stream))
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
        self.total_stream = rx.subjects.BehaviorSubject(0)
        self._amountStream_stream.scan(  # getting AddStreamPair
            __AccumulateDiffStreams,
            dict()
        ).map(  # getting dict of amountStreams:diffStreams
            lambda cAmountToDiffStreams: list(cAmountToDiffStreams.values())
        ).switch_map(  # getting collection of difference streams
            __TryMerge
        ).scan(  # getting merged difference stream
            lambda accumulator, value: BV.MakeValid_Money(accumulator + value),
            0
        ).subscribe(self.total_stream)


class List_TotalStream(TotalStream_Inheritable, List_AmountStreamStream):
    pass


class Dict_TotalStream(TotalStream_Inheritable, Dict_AmountStreamStream):
    pass


class BalanceEntry():
    def __init__(self, parent):
        self.parent = parent
        self._category = self.parent.vModel.Categories["<Default Category>"]
        self.amount_stream = rx.subjects.BehaviorSubject(0)
        self.parent.total_stream.map(
            lambda total: -total
        ).subscribe(self.amount_stream)  # FIX: Is this subscription leaking?

    @property
    def amount(self):
        return self.amount_stream.value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        assert isinstance(value, BV.Model.Category)
        self._category = value
