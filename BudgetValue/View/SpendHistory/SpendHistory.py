import tkinter as tk
from tkinter import ttk
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
from .Table import Table
import BudgetValue as BV
from .. import WidgetFactories as WF
from ..BudgetedTable import BudgetedTable  # noqa
from ..Popup_InputAmount import Popup_InputAmount  # noqa


class SpendHistory(tk.Frame):
    name = "Spend From Categories"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        # Frame of tables
        self.vFrameOfTables = tk.Frame(self)
        self.vFrameOfTables.pack(side=tk.TOP, anchor='w')
        # BudgetedTable
        self.vBTCanvas = tk.Canvas(self.vFrameOfTables, highlightthickness=0)
        self.vBTCanvas.pack(side=tk.LEFT, fill='x', anchor='nw')
        self.vBTTable = BudgetedTable(self.vBTCanvas, vModel)
        self.vBTCanvas.create_window((0, 0), window=self.vBTTable, anchor='nw')
        self.vBTTable.pack(anchor='nw')
        self.vBTTable.Refresh()
        # Verticle Separator
        self.vVerticleSeparator = tk.Frame(self.vFrameOfTables, width=20)
        self.vVerticleSeparator.pack(side=tk.LEFT, anchor='nw', fill='both')
        # Table
        self.vCanvas = tk.Canvas(self.vFrameOfTables, highlightthickness=0)
        self.vCanvas.pack(side=tk.LEFT, fill='x', anchor='nw')
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        self.vTable.pack(anchor='nw')
        self.vTable.Refresh()
        # ButtonBar Buttons

        def AddSpend(amount):
            self.vModel.TransactionHistory.AddTransaction(amount=-amount, bSpend=True, description="nonverified spend")
            self.vTable.Refresh()
        WF.MakeButton(self.vButtonBar, text="Add Unverified Spend", command=lambda: AddSpend(0))
        vButton_Refresh = ttk.Button(self.vButtonBar, text="Refresh",
                                     command=lambda self=self: self.Refresh())
        vButton_Refresh.pack(side=tk.LEFT, anchor='w')

    def Refresh(self):
        self.vBTTable.Refresh()
        self.vTable.Refresh()
