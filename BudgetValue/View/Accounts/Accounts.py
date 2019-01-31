import tkinter as tk
from tkinter import ttk
from .AccountsTable import AccountsTable
import BudgetValue as BV
from .BudgetedTable import BudgetedTable


class Accounts(tk.Frame):
    name = "Double Check Totals"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.bind("<Destroy>", lambda event: self._destroy())
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        vButton_AddRow = ttk.Button(self.vButtonBar, text="AddRow",
                                    command=lambda self=self: self.AddRow())
        vButton_AddRow.pack(side=tk.LEFT, anchor='w')
        vButton_TriggerNonDistinctChange = ttk.Button(self.vButtonBar, text="TriggerChange",
                                                      command=lambda self=self: self.TriggerChange())
        vButton_TriggerNonDistinctChange.pack(side=tk.LEFT, anchor='w')
        # Frame of both tables
        self.vFrameOfBothTables = tk.Frame(self)
        self.vFrameOfBothTables.pack(side=tk.TOP, anchor='w')
        # BudgetedTable
        self.vBudgetedTableCanvas = tk.Canvas(self.vFrameOfBothTables, highlightthickness=0)
        self.vBudgetedTableCanvas.pack(side=tk.LEFT, anchor='nw')
        self.vBudgetedTable = BudgetedTable(self.vBudgetedTableCanvas, vModel)
        self.vBudgetedTableCanvas.create_window((0, 0), window=self.vBudgetedTable, anchor='nw')
        self.vBudgetedTable.pack(anchor='nw')
        self.vBudgetedTable.Refresh()
        # Verticle Separator
        self.vVerticleSeparator = tk.Frame(self.vFrameOfBothTables, width=20)
        self.vVerticleSeparator.pack(side=tk.LEFT, anchor='nw', fill='both')
        # AccountsTable
        self.vCanvas = tk.Canvas(self.vFrameOfBothTables, highlightthickness=0)
        self.vCanvas.pack(side=tk.LEFT, fill='x', anchor='nw')
        self.vAccountsTable = AccountsTable(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vAccountsTable, anchor='nw')
        self.vAccountsTable.pack(anchor='nw')
        self.vAccountsTable.Refresh()

    def TriggerChange(self):
        if len(self.vModel.Accounts) > 2:
            self.vModel.Accounts[0], self.vModel.Accounts[1] = self.vModel.Accounts[1], self.vModel.Accounts[0]
        self.vAccountsTable.Refresh()

    def AddRow(self):
        self.vModel.Accounts.AddRow()
        self.vAccountsTable.Refresh()

    def _destroy(self):
        self.vModel.Accounts.Save()
