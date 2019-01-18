import tkinter as tk
from tkinter import ttk
import tkinter.filedialog  # noqa
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import tkinter.messagebox  # noqa
from .Table import Table
import BudgetValue as BV


class Spendables(tk.Frame):
    name = "Spendables"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.bind("<Destroy>", lambda event: self._destroy())
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        vButton_AddRow = ttk.Button(self.vButtonBar, text="AddPaycheckHistoryColumn",
                                    command=lambda self=self: self.AddPaycheckHistoryColumn())
        vButton_AddRow.pack(side=tk.LEFT, anchor='w')
        vButton_AddPaycheckPlan = ttk.Button(self.vButtonBar, text="AddPaycheckPlan",
                                             command=lambda self=self: self.AddPaycheckPlan())
        vButton_AddPaycheckPlan.pack(side=tk.LEFT, anchor='w')
        vButton_Clear = ttk.Button(self.vButtonBar, text="Clear",
                                   command=lambda self=self: self.Clear())
        vButton_Clear.pack(side=tk.LEFT, anchor='w')
        vButton_Print = ttk.Button(self.vButtonBar, text="Print",
                                   command=lambda self=self: self.Print())
        vButton_Print.pack(side=tk.LEFT, anchor='w')
        # Table
        self.vCanvas = tk.Canvas(self, highlightthickness=0)
        self.vCanvas.pack(side=tk.TOP, fill='x', anchor='nw')
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        self.vTable.pack(anchor='nw')
        # ButtonBar More
        vButton_Refresh = ttk.Button(self.vButtonBar, text="Refresh",
                                     command=lambda self=self: self.vTable.Refresh())
        vButton_Refresh.pack(side=tk.LEFT, anchor='w')

    def Print(self):
        print("self.vModel.PaycheckHistory..")
        for i, cColumn in enumerate(self.vModel.PaycheckHistory):
            print(" Column "+str(i))
            for vEntry in cColumn:
                print("  "+vEntry.category.name+" - "+str(vEntry.amount))

    def Clear(self):
        self.vModel.PaycheckHistory.Clear()
        self.vTable.Refresh()

    def _destroy(self):
        self.vModel.PaycheckHistory.Save()

    def AddPaycheckPlan(self):
        self.vModel.PaycheckHistory.AddPaycheckPlanColumn()
        self.vTable.Refresh()

    def AddPaycheckHistoryColumn(self):
        self.vModel.PaycheckHistory.AddColumn()
        self.vTable.Refresh()
