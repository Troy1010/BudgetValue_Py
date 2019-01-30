import BudgetValue as BV
import rx


class BudgetedSpendables():
    def __init__(self, vModel):
        assert(isinstance(vModel, BV.Model.Model))
        self.vModel = vModel
        # Determine cCategoryTotalStreams, total_stream
        self.cCategoryTotalStreams = dict()
        self.total_stream = rx.subjects.BehaviorSubject(0)

        for category in self.vModel.Categories.Select(types_exclude=BV.Model.CategoryType.income):
            # create category_total_stream
            self.cCategoryTotalStreams[category.name] = rx.subjects.BehaviorSubject(0)
            # hook category_total_stream into total_stream
            self.cCategoryTotalStreams[category.name].distinct_until_changed().pairwise().map(
                lambda cPair: cPair[1]-cPair[0]
            ).subscribe(lambda diff: self.total_stream.on_next(BV.MakeValid_Money(self.total_stream.value + diff)))
            # feed category_total_stream
            rx.Observable.combine_latest(
                self.vModel.SplitMoneyHistory.cCategoryTotalStreams[category.name],
                self.vModel.SpendingHistory.cCategoryTotalStreams[category.name],
                lambda x, y: BV.MakeValid_Money(x+y)
            ).subscribe(self.cCategoryTotalStreams[category.name])
