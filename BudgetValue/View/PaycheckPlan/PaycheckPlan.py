from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
from BudgetValue.View import Fonts


class PaycheckPlan(tk.Frame):
    name = "Paycheck Plan"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)

        for i, vCategory in enumerate(vModel.Categories.GetTrueCategories()):
            b = tk.Text(self, font=Fonts.FONT_SMALL, width=15,
                        borderwidth=2, height=1, relief='ridge', background='SystemButtonFace')
            b.insert(1.0, str(vCategory.name))
            b.grid(row=i)
            b.configure(state="disabled")
