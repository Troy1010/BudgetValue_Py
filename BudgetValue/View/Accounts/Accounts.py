import tkinter as tk
from .AccountsTable import AccountsTable
import BudgetValue as BV
from .Difference import Difference
from .. import WidgetFactories as WF
from ..CategoryTable import CategoryTable


class Accounts(tk.Frame):
    name = "Double Check Totals"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        vButton_AddRow = WF.MakeButton(self.vButtonBar, text="Add Row",
                                       command=lambda self=self: self.AddRow())
        vButton_AddRow.pack(side=tk.LEFT, anchor='w')
        # Frame of tables
        self.vFrameOfTables = tk.Frame(self)
        self.vFrameOfTables.pack(side=tk.TOP, anchor='w')
        # BudgetedTable
        self.vBudgetedTableCanvas = tk.Canvas(self.vFrameOfTables, highlightthickness=0)
        self.vBudgetedTableCanvas.pack(side=tk.LEFT, anchor='nw')
        self.vBudgetedTable = CategoryTable(self.vBudgetedTableCanvas, vModel)
        self.vBudgetedTableCanvas.create_window((0, 0), window=self.vBudgetedTable, anchor='nw')
        self.vBudgetedTable.pack(anchor='nw')
        self.vBudgetedTable.Refresh()
        # Verticle Separator
        self.vVerticleSeparator = tk.Frame(self.vFrameOfTables, width=20)
        self.vVerticleSeparator.pack(side=tk.LEFT, anchor='nw', fill='both')
        # AccountsTable
        self.vAccountsCanvas = tk.Canvas(self.vFrameOfTables, highlightthickness=0)
        self.vAccountsCanvas.pack(side=tk.LEFT, fill='x', anchor='nw')
        self.vAccountsTable = AccountsTable(self.vAccountsCanvas, vModel)
        self.vAccountsCanvas.create_window((0, 0), window=self.vAccountsTable, anchor='nw')
        self.vAccountsTable.pack(anchor='nw')
        self.vAccountsTable.Refresh()
        # Verticle Separator
        self.vVerticleSeparator = tk.Frame(self.vFrameOfTables, width=20)
        self.vVerticleSeparator.pack(side=tk.LEFT, anchor='nw', fill='both')
        # Difference
        self.vDifferenceCanvas = tk.Canvas(self.vFrameOfTables, highlightthickness=0)
        self.vDifferenceCanvas.pack(side=tk.LEFT, fill='x', anchor='nw')
        self.vDifference = Difference(self.vDifferenceCanvas, vModel)
        self.vDifferenceCanvas.create_window((0, 0), window=self.vDifference, anchor='nw')
        self.vDifference.pack(anchor='nw')
        self.vDifference.Refresh()

    def AddRow(self):
        self.vModel.Accounts.AddRow()
        self.vAccountsTable.Refresh()
