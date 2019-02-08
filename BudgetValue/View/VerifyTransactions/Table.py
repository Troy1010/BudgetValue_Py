import TM_CommonPy as TM  # noqa
import BudgetValue as BV  # noqa
import tkinter as tk
from BudgetValue.View import WidgetFactories as WF  # noqa
from BudgetValue.View.Skin import vSkin  # noqa
from .. import Misc
from BudgetValue.Model.Categories import Categories  # noqa


class Table(Misc.ModelTable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vModel.TransactionHistory._merged_amountStream_stream.subscribe(lambda x: print("_merged_amountStream_stream`did something"))
        self.vModel.TransactionHistory._merged_amountStream_stream.subscribe(self.Refresh())

    def Refresh(self):
        super().Refresh()
        # Header
        WF.MakeHeader(self, (0, 1), text="Timestamp")
        WF.MakeHeader(self, (0, 2), text="Category")
        WF.MakeHeader(self, (0, 3), text="Amount")
        WF.MakeHeader(self, (0, 4), text="Description")
        # Data
        for row, transaction in enumerate(self.vModel.TransactionHistory, self.iFirstDataRow):
            assert isinstance(transaction, BV.Model.Transaction)
            self.MakeEntry_Timestamp((row, 1), transaction=transaction, stream=transaction.timestamp_stream, justify=tk.LEFT)
            self.MakeEntry_Category((row, 2), transaction=transaction, text=transaction.GetCategorySummary(), justify=tk.LEFT)
            WF.MakeEntry(self, (row, 3), stream=transaction.amount_stream, validation=BV.MakeValid_Money, justify=tk.RIGHT)
            WF.MakeEntry(self, (row, 4), stream=transaction.description_stream, justify=tk.LEFT)
            WF.MakeX(self, (row, 5), lambda transaction=transaction: (self.vModel.TransactionHistory.RemoveTransaction(transaction), self.Refresh())[0])

    def MakeEntry_Timestamp(self, cRowColumnPair, transaction, stream, justify=tk.RIGHT):
        w = WF.MakeEntry(self, cRowColumnPair, stream=stream, justify=justify, bEditableState=False, validation=BV.ValidateTimestamp, display=BV.DisplayTimestamp)

        def DestroyHandler(w, background):
            try:
                w.config(readonlybackground=background)
            except tk.TclError:  # w does not exist
                pass

        def AssignTimestamp(transaction, timestamp):
            transaction.timestamp = timestamp
        w.bind('<Button-1>', lambda event, w=w, x=self.winfo_rootx(), y=self.winfo_rooty(): (
            BV.View.Popup_SelectDate(self.winfo_toplevel(),
                                     lambda timestamp, transaction=transaction: AssignTimestamp(transaction, timestamp),
                                     transaction.timestamp,
                                     vDestroyHandler=lambda w=w, background=w['background']: DestroyHandler(w, background)
                                     ),
            w.config(readonlybackground="grey")
        ))

    def MakeEntry_Category(self, cRowColumnPair, transaction, text, justify=tk.RIGHT):
        w = WF.MakeEntry(self, cRowColumnPair, text=text, justify=justify, bEditableState=False)

        def DestroyHandler(w, background):
            try:
                w.config(readonlybackground=background)
            except tk.TclError:  # w does not exist
                pass

        def CategoryHandler(transaction, category):
            transaction.SetOneCategory(category)
            self.Refresh()
        w.bind('<Button-1>', lambda event, w=w, x=self.winfo_rootx(), y=self.winfo_rooty(): (
            BV.View.Popup_SelectCategory(self.winfo_toplevel(),
                                         lambda category, transaction=transaction: CategoryHandler(transaction, category),
                                         self.vModel.Categories.values(),
                                         vDestroyHandler=lambda w=w, background=w['background']: DestroyHandler(w, background)
                                         ),
            w.config(readonlybackground="grey")
        ))
