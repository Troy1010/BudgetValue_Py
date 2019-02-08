import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import BudgetValue as BV  # noqa
from BudgetValue.View import WidgetFactories as WF  # noqa
from BudgetValue.View.Skin import vSkin  # noqa
from .. import Misc  # noqa
from BudgetValue._Logger import Log  # noqa


class Table(Misc.ModelTable):

    def Refresh(self):
        super().Refresh()
        # Header
        WF.MakeHeader(self, (0, 1), text="Timestamp")
        WF.MakeHeader(self, (0, 2), text="Category")
        WF.MakeHeader(self, (0, 3), text="Amount")
        WF.MakeHeader(self, (0, 4), text="Description")
        # Data
        for row, spend in enumerate(self.vModel.TransactionHistory.Iter_Spend(), self.iFirstDataRow):
            assert isinstance(spend, BV.Model.Transaction)
            self.MakeEntry_Timestamp((row, 1), spend=spend, stream=spend.timestamp_stream, justify=tk.LEFT)
            self.MakeEntry_Category((row, 2), spend=spend, text=spend.GetCategorySummary(), justify=tk.LEFT)
            WF.MakeEntry(self, (row, 3), stream=spend.amount_stream, validation=BV.MakeValid_Money_Negative, justify=tk.RIGHT)
            WF.MakeEntry(self, (row, 4), stream=spend.description_stream, justify=tk.LEFT)
            WF.MakeX(self, (row, 5), lambda spend=spend: (self.vModel.TransactionHistory.RemoveTransaction(spend), self.Refresh())[0])

    def MakeEntry_Timestamp(self, cRowColumnPair, spend, stream, justify=tk.RIGHT):
        w = WF.MakeEntry(self, cRowColumnPair, stream=stream, justify=justify, bEditableState=False, validation=BV.ValidateTimestamp, display=BV.DisplayTimestamp)

        def DestroyHandler(w, background):
            try:
                w.config(readonlybackground=background)
            except tk.TclError:  # w does not exist
                pass

        def AssignTimestamp(spend, timestamp):
            spend.timestamp = timestamp
        w.bind('<Button-1>', lambda event, w=w, x=self.winfo_rootx(), y=self.winfo_rooty(): (
            BV.View.Popup_SelectDate(self.winfo_toplevel(),
                                     lambda timestamp, spend=spend: AssignTimestamp(spend, timestamp),
                                     spend.timestamp,
                                     vDestroyHandler=lambda w=w, background=w['background']: DestroyHandler(w, background)
                                     ),
            w.config(readonlybackground="grey")
        ))

    def MakeEntry_Category(self, cRowColumnPair, spend, text, justify=tk.RIGHT):
        w = WF.MakeEntry(self, cRowColumnPair, text=text, justify=justify, bEditableState=False)

        def DestroyHandler(w, background):
            try:
                w.config(readonlybackground=background)
            except tk.TclError:  # w does not exist
                pass

        def CategoryHandler(spend, category):
            spend.SetOneCategory(category)
            self.Refresh()
        w.bind('<Button-1>', lambda event, w=w, x=self.winfo_rootx(), y=self.winfo_rooty(): (
            BV.View.Popup_SelectCategory(self.winfo_toplevel(),
                                         lambda category, spend=spend: CategoryHandler(spend, category),
                                         self.vModel.Categories.values(),
                                         vDestroyHandler=lambda w=w, background=w['background']: DestroyHandler(w, background)
                                         ),
            w.config(readonlybackground="grey")
        ))
