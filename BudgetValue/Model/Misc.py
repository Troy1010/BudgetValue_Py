import BudgetValue as BV
import rx


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
