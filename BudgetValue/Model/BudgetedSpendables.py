import BudgetValue as BV
import rx


class BudgetedSpendables():
    def __init__(self, vModel):
        assert(isinstance(vModel, BV.Model.Model))
        self.vModel = vModel
        # Determine cCategoryTotalStreams, total_stream
        self.cCategoryTotalStreams = dict()
        self.total_stream = rx.subjects.BehaviorSubject(0)
        for categoryName in self.vModel.Categories.keys():
            self.cCategoryTotalStreams[categoryName] = rx.subjects.BehaviorSubject(0)
            self.cCategoryTotalStreams[categoryName].distinct_until_changed().pairwise().map(
                lambda cOldNewPair: cOldNewPair[1]-cOldNewPair[0]
            ).subscribe(lambda diff: self.total_stream.on_next(self.total_stream.value + diff))
            rx.Observable.combine_latest(
                self.vModel.SplitMoneyHistory.cCategoryTotalStreams[categoryName],
                self.vModel.SpendingHistory.cCategoryTotalStreams[categoryName],
                lambda x, y: BV.MakeValid_Money(x+y)
            ).subscribe(self.cCategoryTotalStreams[categoryName])
