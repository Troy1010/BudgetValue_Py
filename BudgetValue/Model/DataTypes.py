import BudgetValue as BV
import rx
import TM_CommonPy as TM  # noqa


class CollectionEditInfo():
    def __init__(self, bAdd, key, value):
        self.key = key
        self.value = value
        self.bAdd = bAdd


class Dict_ValueStream(dict):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._value_stream = rx.subjects.Subject()

    def __setitem__(self, key, value):
        # if we have an old value and it isn't the new value, remove old value
        if key in self and self[key] != value:
            self._value_stream.on_next(CollectionEditInfo(False, key, self[key]))
        #
        bNewValueIsOldValue = key in self and self[key] == value
        super().__setitem__(key, value)
        # if new value isn't the old value, add that new value
        if not bNewValueIsOldValue:
            self._value_stream.on_next(CollectionEditInfo(True, key, value))

    def __delitem__(self, key):
        if key in self:
            self._value_stream.on_next(CollectionEditInfo(False, key, self[key]))
        super().__delitem__(key)

    def clear(self):
        # make sure __delitem__ is triggered
        for key in list(self.keys()):
            del self[key]
        #
        super().clear()


class List_ValueStream(list):
    def __init__(self, *args, **kwargs):
        self._value_stream = rx.subjects.Subject()
        super().__init__()

    def __setitem__(self, key, value):
        # if value isn't old, remove the old and add the new
        if key in self and self[key] != value:
            if hasattr(self[key], 'destroy'):
                self[key].destroy()
            self._value_stream.on_next(CollectionEditInfo(False, key, self[key]))
        super().__setitem__(key, value)
        self._value_stream.on_next(CollectionEditInfo(True, key, value))

    def remove(self, value):
        if hasattr(value, 'destroy'):
            value.destroy()
        self._value_stream.on_next(CollectionEditInfo(False, super().index(value), value))
        super().remove(value)

    def insert(self, index, value):
        super().insert(index, value)
        self._value_stream.on_next(CollectionEditInfo(True, index, value))

    def append(self, value):
        super().append(value)
        self._value_stream.on_next(CollectionEditInfo(True, -1, value))

    def __delitem__(self, key):
        if hasattr(self[key], 'destroy'):
            self[key].destroy()
        self._value_stream.on_next(CollectionEditInfo(False, key, self[key]))
        super().__delitem__(key)

    def clear(self):
        # make sure __delitem__ is triggered
        while(len(self)):
            del self[-1]
        #
        super().clear()


class StreamInfo():
    def __init__(self, bAdd, stream, category_name, transaction=None):
        self.bAdd = bAdd
        self.stream = stream
        self.category_name = category_name
        self.transaction = transaction


class AmountStreamStream():
    # requires _value_stream
    def __init__(self, *args, **kwargs):
        super().__init__()
        # Feed _amountStream_stream
        self._amountStream_stream = rx.subjects.Subject()

        def OnValueStreamEdit(col_edit_info):
            assert isinstance(col_edit_info, CollectionEditInfo)
            if hasattr(col_edit_info.value, 'amount_stream') and not isinstance(col_edit_info.value, BalanceEntry):
                if not col_edit_info.bAdd:
                    col_edit_info.value.amount_stream.on_completed()
                self._amountStream_stream.on_next(StreamInfo(col_edit_info.bAdd, col_edit_info.value.amount_stream, col_edit_info.key))
        self._value_stream.subscribe(OnValueStreamEdit)


class DiffStreamCategoryNamePair():
    def __init__(self, diffStream, category_name):
        self.diffStream = diffStream
        self.category_name = category_name


class DiffStreams_Inheritable():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def __AccumulateDiffStreams(accumulator, value):
            assert(isinstance(value, StreamInfo))
            if value.bAdd:
                accumulator[value.stream] = DiffStreamCategoryNamePair(value.stream.distinct_until_changed().pairwise().map(lambda cOldNewPair: cOldNewPair[1]-cOldNewPair[0]), value.category_name)
            else:
                if value.stream in accumulator:
                    del accumulator[value.stream]
            return accumulator

        self._diffStreamCollection_stream = self._amountStream_stream.scan(  # getting StreamInfo
            __AccumulateDiffStreams,
            dict()
        ).publish().ref_count()


class CategoryTotalStreams_Inheritable():
    def __init__(self, vModel, *args, **kwargs):
        super().__init__(vModel, *args, **kwargs)
        self.vModel = vModel

        def __TryMerge(cStreams):
            if not cStreams:  # all streams are empty
                return rx.Observable.of(0)
            else:
                return rx.Observable.merge(cStreams)

        # Determine cCategoryTotalStreams
        self.cCategoryTotalStreams = dict()
        for category_name in self.vModel.Categories.keys():
            self.cCategoryTotalStreams[category_name] = rx.subjects.BehaviorSubject(0)
        # stream updates to cCategoryTotalStreams
        for category_name, categoryTotal_stream in self.cCategoryTotalStreams.items():
            self._diffStreamCollection_stream.map(  # getting dict of amountStreams:diffStreamCategoryNamePair
                lambda cAmountToDiffStreamCategoryNamePair, category_name=category_name: (
                    {k: v for k, v in cAmountToDiffStreamCategoryNamePair.items() if v.category_name == category_name}
                )
            ).map(  # getting dict of amountStreams:diffStreamCategoryNamePair for only this category
                lambda cAmountToDiffStreamCategoryNamePair: [x.diffStream for x in cAmountToDiffStreamCategoryNamePair.values()]
            ).switch_map(  # getting collection of difference streams
                __TryMerge
            ).scan(  # getting merged difference stream
                lambda accumulator, value: BV.MakeValid_Money(accumulator + value),
                0
            ).subscribe(categoryTotal_stream)


class TotalStream_Inheritable():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        def __TryMerge(cStreams):
            if not cStreams:  # all streams are empty
                return rx.Observable.of(0)
            else:
                return rx.Observable.merge(cStreams)
        self.total_stream = rx.subjects.BehaviorSubject(0)
        self._diffStreamCollection_stream.map(  # getting dict of amountStreams:diffStreamCategoryNamePair
            lambda cAmountToDiffStreamCategoryNamePair: [x.diffStream for x in cAmountToDiffStreamCategoryNamePair.values()]
        ).switch_map(  # getting collection of difference streams
            __TryMerge
        ).scan(  # getting merged difference stream
            lambda accumulator, value: BV.MakeValid_Money(accumulator + value),
            0
        ).publish().ref_count().subscribe(self.total_stream)


class List_TotalStream(TotalStream_Inheritable, DiffStreams_Inheritable, AmountStreamStream, List_ValueStream):
    pass


class Dict_TotalStream(TotalStream_Inheritable, DiffStreams_Inheritable, AmountStreamStream, Dict_ValueStream):
    pass


class BalanceEntry():
    def __init__(self, parent, total_stream):
        self.parent = parent
        self._category = BV.Model.Categories.default_category
        self.amount_stream = rx.subjects.BehaviorSubject(0)
        total_stream.map(
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
