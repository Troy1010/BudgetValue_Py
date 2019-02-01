import tkinter as tk
from tkinter import ttk
import tkinter.filedialog  # noqa
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import tkinter.messagebox  # noqa
from .Table import Table
import BudgetValue as BV
from .. import WidgetFactories as WF


class SpendingHistory(tk.Frame):
    name = "Spend From Categories"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.bind("<Destroy>", lambda event: self._destroy())
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        vButton_AddColumn = WF.MakeButton(self.vButtonBar, text="Add Column",
                                          command=lambda self=self: self.AddSpendingHistoryColumn())
        vButton_AddColumn.pack(side=tk.LEFT, anchor='w')
        # Table
        self.vCanvas = tk.Canvas(self, highlightthickness=0)
        self.vCanvas.pack(side=tk.TOP, fill='x', anchor='nw')
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        self.vTable.pack(anchor='nw')
        self.vTable.Refresh()
        # ButtonBar More
        vButton_Refresh = ttk.Button(self.vButtonBar, text="Refresh",
                                     command=lambda self=self: self.vTable.Refresh())
        vButton_Refresh.pack(side=tk.LEFT, anchor='w')

    def _destroy(self):
        self.vModel.SpendingHistory.Save()

    def AddSpendingHistoryColumn(self):
        self.vModel.SpendingHistory.AddColumn()
        self.vTable.Refresh()
