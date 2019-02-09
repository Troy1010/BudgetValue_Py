import BudgetValue as BV
import rx


class Budgeted():
    def __init__(self, vModel):
        assert(isinstance(vModel, BV.Model.Model))
        self.vModel = vModel
        # Determine cCategoryTotalStreams, total_stream
        self.total_stream = rx.subjects.BehaviorSubject(0)
        self.cCategoryTotalStreams = {}
        # Subscribe CategoryTotals
        self.cDisposables_CT = {}
        self.cDisposableCount_CT = {}

        def FeedCategoryTotals(stream_info):
            if stream_info.bAdd:
                # add category to cCategoryTotalStreams if it's absent
                if stream_info.categoryName not in self.cCategoryTotalStreams:
                    self.cCategoryTotalStreams[stream_info.categoryName] = rx.subjects.BehaviorSubject(0)
                # subscribe cCategoryTotalStreams
                self.cDisposables_CT[stream_info.stream] = stream_info.stream.distinct_until_changed().pairwise().map(lambda cOldNewPair: cOldNewPair[1]-cOldNewPair[0]).subscribe(
                    lambda diff:
                        self.cCategoryTotalStreams[stream_info.categoryName].on_next(
                            self.cCategoryTotalStreams[stream_info.categoryName].value + diff
                        )
                )
                # keep track of how many subscriptions this category has
                if stream_info.categoryName not in self.cDisposableCount_CT:
                    self.cDisposableCount_CT[stream_info.categoryName] = 0
                self.cDisposableCount_CT[stream_info.categoryName] += 1
            else:
                # dispose of cCategoryTotalStreams subscription
                self.cDisposables_CT[stream_info.stream].dispose()
                del self.cDisposables_CT[stream_info.stream]
                # if every subscription of this category has been disposed, delete it.
                self.cDisposableCount_CT[stream_info.categoryName] -= 1
                if self.cDisposableCount_CT[stream_info.categoryName] == 0:
                    del self.cCategoryTotalStreams[stream_info.categoryName]
        self.vModel.TransactionHistory._merged_amountStream_stream.subscribe(FeedCategoryTotals)
        # Subscribe total_stream
        self.cDisposables_TS = {}

        def FeedTotal(stream_info):
            if stream_info.bAdd:
                self.cDisposables_TS[stream_info.stream] = stream_info.stream.distinct_until_changed().pairwise().map(lambda cOldNewPair: cOldNewPair[1]-cOldNewPair[0]).subscribe(
                    lambda diff:
                        self.total_stream.on_next(
                            self.total_stream.value + diff
                        )
                )
            else:
                self.cDisposables_TS[stream_info.stream].dispose()
                del self.cDisposables_TS[stream_info.stream]
        self.vModel.TransactionHistory._merged_amountStream_stream.subscribe(FeedTotal)
