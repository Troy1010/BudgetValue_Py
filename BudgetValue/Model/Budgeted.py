import BudgetValue as BV


class Budgeted():
    def __init__(self, vModel):
        assert(isinstance(vModel, BV.Model.Model))
        self.vModel = vModel
        # Determine cCategoryTotalStreams, total_stream
        self.cCategoryTotalStreams = self.vModel.TransactionHistory.cCategoryTotals
        self.total_stream = self.vModel.TransactionHistory.total_stream
