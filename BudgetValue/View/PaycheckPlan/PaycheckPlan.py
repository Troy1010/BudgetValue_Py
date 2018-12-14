from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
from tkinter import ttk
from .Table import Table
import BudgetValue as BV


class PaycheckPlan(tk.Frame):
    name = "Paycheck Plan"

    def __init__(self, parent, vModel):
        assert isinstance(vModel, BV.Model.Model)
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
        self.bind("<Destroy>", lambda event, self=self: self._destroy(event))
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        vButton_Save = ttk.Button(self.vButtonBar, text="Save",
                                  command=lambda self=self: self.vModel.PaycheckPlan.Save())
        vButton_Save.pack(side=tk.LEFT, anchor='w')
        vButton_Load = ttk.Button(self.vButtonBar, text="Load",
                                  command=lambda self=self: self.Load())
        vButton_Load.pack(side=tk.LEFT, anchor='w')
        vButton_Print = ttk.Button(self.vButtonBar, text="Print",
                                   command=lambda self=self: print(self.vModel.PaycheckPlan.Narrate()))
        vButton_Print.pack(side=tk.LEFT, anchor='w')
        # Table
        self.vCanvas = tk.Canvas(self, highlightthickness=0)
        self.vCanvas.pack(side=tk.TOP, fill='x', anchor='nw')
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        self.vTable.pack(anchor='nw')
        self.Load()

    def _destroy(self, event):
        self.vModel.PaycheckPlan.Save()

    def Load(self):
        self.vModel.PaycheckPlan.Load()
        self.vTable.Refresh()
