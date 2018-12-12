from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
from tkinter import ttk
from .Table import Table


class PaycheckPlan(tk.Frame):
    name = "Paycheck Plan"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
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
        self.vTable = Table(self, vModel)
        self.vTable.pack(side=tk.TOP, expand=True, fill="both")

    def Load(self):
        self.vModel.PaycheckPlan.Load()
        self.vTable.Refresh()
