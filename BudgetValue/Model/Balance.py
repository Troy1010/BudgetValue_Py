import BudgetValue as BV
import rx


class Balance():
    def __init__(self, vModel):
        assert(isinstance(vModel, BV.Model.Model))
        self.vModel = vModel
        # Determine balance_stream
        self.balance_stream = rx.subjects.BehaviorSubject(0)
        rx.Observable.combine_latest(
            self.vModel.Budgeted.total_stream,
            self.vModel.Accounts.total_stream,
            lambda x, y: BV.MakeValid_Money(x-y)
        ).subscribe(self.balance_stream)
