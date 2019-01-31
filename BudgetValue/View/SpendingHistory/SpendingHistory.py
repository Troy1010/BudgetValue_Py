import tkinter as tk
from tkinter import ttk
import tkinter.filedialog  # noqa
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import tkinter.messagebox  # noqa
from .Table import Table
import BudgetValue as BV


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
        vButton_AddRow = ttk.Button(self.vButtonBar, text="Split",
                                    command=lambda self=self: self.AddSpendingHistoryColumn())
        vButton_AddRow.pack(side=tk.LEFT, anchor='w')
        #
        vButton_Print = ttk.Button(self.vButtonBar, text="Print",
                                   command=lambda self=self: self.Print())
        vButton_Print.pack(side=tk.LEFT, anchor='w')
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

    def Print(self):
        print("self.vModel.SpendingHistory..")
        for i, cColumn in enumerate(self.vModel.SpendingHistory):
            print(" Column "+str(i))
            for vEntry in cColumn:
                print("  "+vEntry.category.name+" - "+str(vEntry.amount))

    def _destroy(self):
        self.vModel.SpendingHistory.Save()

    def AddSpendingHistoryColumn(self):
        self.vModel.SpendingHistory.AddColumn()
        self.vTable.Refresh()
