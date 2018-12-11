from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
from .Table import Table


class PaycheckPlan(tk.Frame):
    name = "Paycheck Plan"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
        # Table
        self.vTable = Table(self, vModel)
        self.vTable.pack(side=tk.TOP, expand=True, fill="both")
