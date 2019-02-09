import tkinter as tk
from tkinter import ttk
import tkinter.filedialog  # noqa
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
from .Table import Table
import BudgetValue as BV
import rx
from .. import WidgetFactories as WF
from ..Skin import vSkin
from ...Model.Categories import Categories  # noqa
from ..Popup_InputAmount import Popup_InputAmount


class SplitMoneyIntoCategories(tk.Frame):
    name = "Split Money Into Categories"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')

        def CreateTransaction(amount):
            self.vModel.TransactionHistory.AddTransaction(bSpend=False, amount=amount)
            self.vTable.Refresh()
        vButton_SplitPaycheck = ttk.Button(self.vButtonBar, text="Add Unverified Income",
                                           command=lambda: Popup_InputAmount(self, self.vModel, lambda amount: CreateTransaction(amount)))
        vButton_SplitPaycheck.pack(side=tk.LEFT, anchor='w')
        # Button_SplitDifference
        vSplitDifferenceText_stream = rx.subjects.BehaviorSubject("")
        self.vModel.Balance.balance_stream.map(
            lambda balance: "Add Unverified Income - Difference (" + str(balance) + ")"
        ).subscribe(vSplitDifferenceText_stream)

        def SplitDifference():
            self.vModel.TransactionHistory.AddTransaction(amount=-self.vModel.Balance.balance_stream.value, bSpend=False)
            self.vTable.Refresh()
        vButton_SplitDifference = WF.MakeButton(self.vButtonBar, stream=vSplitDifferenceText_stream,
                                                command=lambda self=self: SplitDifference())

        def HighlightBalanceButton(balance):
            if balance:
                vButton_SplitDifference.config(background=vSkin.BG_BAD)
            else:
                vButton_SplitDifference.config(background=vSkin.BG_DEFAULT)
        self.vModel.Balance.balance_stream.subscribe(HighlightBalanceButton)
        # Table
        self.vCanvas = tk.Canvas(self, highlightthickness=0)
        self.vCanvas.pack(side=tk.TOP, fill='x', anchor='nw')
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        self.vTable.pack(anchor='nw')
        self.vTable.Refresh()
        # ButtonBar More
        WF.MakeButton(self.vButtonBar, text="Refresh", command=lambda: self.vTable.Refresh())
        WF.MakeButton(self.vButtonBar, text="Import Transactions", command=lambda: 1)
