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
        for row, spend in enumerate(self.vModel.SpendHistory, self.iFirstDataRow):
            assert(isinstance(spend, BV.Model.Spend))
            self.MakeEntry_Timestamp((row, 1), spend=spend, text=spend.timestamp_stream, justify=tk.LEFT, bTextIsTimestamp=True)
            self.MakeEntry_Category((row, 2), spend=spend, text=spend.category_stream, justify=tk.LEFT)
            self.MakeEntry_Amount((row, 3), spend=spend, text=spend.amount_stream)
            self.MakeEntry_Description((row, 4), spend=spend, text=spend.description_stream, justify=tk.LEFT)
            WF.MakeX(self, (row, 5), lambda spend=spend: (self.vModel.SpendHistory.RemoveSpend(spend), self.Refresh())[0])

    def MakeEntry_Timestamp(self, cRowColumnPair, spend, text, justify=tk.RIGHT, bTextIsTimestamp=True):
        w = WF.MakeEntry(self, cRowColumnPair, text=text, justify=justify, bEditableState=False, bTextIsTimestamp=True)

        def DestroyHandler(w, background):
            try:
                w.config(readonlybackground=background)
            except tk.TclError:  # w does not exist
                pass

        def TimestampHandler(spend, timestamp):
            spend.timestamp = timestamp
        w.bind('<Button-1>', lambda event, w=w, x=self.winfo_rootx(), y=self.winfo_rooty(): (
            BV.View.Popup_SelectDate(self.winfo_toplevel(),
                                     lambda timestamp, spend=spend: TimestampHandler(spend, timestamp),
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
            spend.category = category
        w.bind('<Button-1>', lambda event, w=w, x=self.winfo_rootx(), y=self.winfo_rooty(): (
            BV.View.SelectCategoryPopup(self.winfo_toplevel(),
                                        lambda category, spend=spend: CategoryHandler(spend, category),
                                        self.vModel.Categories.values(),
                                        vDestroyHandler=lambda w=w, background=w['background']: DestroyHandler(w, background)
                                        ),
            w.config(readonlybackground="grey")
        ))

    def MakeEntry_Amount(self, cRowColumnPair, spend, text, justify=tk.RIGHT):
        w = WF.MakeEntry(self, cRowColumnPair, text=text, validation=BV.MakeValid_Money_Negative_ZeroIsNone, justify=justify)

        def AssignAmount(spend, amount):
            spend.amount = amount
        w.bind("<FocusOut>", lambda event, spend=spend: AssignAmount(spend, w.text), add="+")

    def MakeEntry_Description(self, cRowColumnPair, spend, text, justify=tk.RIGHT):
        w = WF.MakeEntry(self, cRowColumnPair, text=text,
                         justify=justify)

        def AssignDescription(spend, description):
            spend.description = description
        w.bind("<FocusOut>", lambda event, spend=spend: AssignDescription(spend, w.text), add="+")
