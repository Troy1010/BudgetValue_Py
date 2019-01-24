import tkinter as tk
from tkinter import ttk
from .Table import Table
import BudgetValue as BV


class NetWorth(tk.Frame):
    name = "Net Worth"

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
        # Table
        self.vCanvas = tk.Canvas(self, highlightthickness=0)
        self.vCanvas.pack(side=tk.TOP, fill='x', anchor='nw')
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        self.vTable.pack(anchor='nw')
        self.vTable.Refresh()

    def TriggerChange(self):
        if len(self.vModel.NetWorth) > 2:
            self.vModel.NetWorth[0], self.vModel.NetWorth[1] = self.vModel.NetWorth[1], self.vModel.NetWorth[0]
        self.vTable.Refresh()

    def AddRow(self):
        self.vModel.NetWorth.AddRow()
        self.vTable.Refresh()

    def _destroy(self):
        self.vModel.NetWorth.Save()
