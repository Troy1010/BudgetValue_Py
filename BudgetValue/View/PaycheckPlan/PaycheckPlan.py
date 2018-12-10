from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
from BudgetValue.View import Fonts


class PaycheckPlan(tk.Frame):
    name = "Paycheck Plan"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel

        for i, category in enumerate(vModel.Categories.GetTrueCategories()):
            self.MakeText((i, 0), category)
            self.MakeEntry((i, 1), category)
            self.MakeEntry((i, 2), category)

    def MakeText(self, cRowColumnPair, category):
        w = tk.Text(self, font=Fonts.FONT_SMALL, width=15,
                    borderwidth=2, height=1, relief='ridge', background='SystemButtonFace')
        w.insert(1.0, category.name)
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])
        w.configure(state="disabled")
        w.category = category

    def MakeEntry(self, cRowColumnPair, category):
        w = tk.Entry(self, font=Fonts.FONT_SMALL, width=15, justify=tk.RIGHT,
                     borderwidth=2, relief='ridge', background='SystemButtonFace')
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])
        w.bind("<FocusIn>", lambda event, w=w: self.Entry_FocusIn(event, w))
        w.bind("<FocusOut>", lambda event, w=w: self.Entry_FocusOut(event, w))
        w.category = category

    def Entry_FocusIn(self, event, w):
        w.config(justify=tk.LEFT)

    def Entry_FocusOut(self, event, w):
        w.config(justify=tk.RIGHT)
        self.SaveCategoryPlan(w)

    def SaveCategoryPlan(self, cell):
        if cell.category not in self.vModel.PaycheckPlan.cCategoryPlans:
            self.vModel.PaycheckPlan.cCategoryPlans[cell.category] = self.vModel.PaycheckPlan.CategoryPlan()
        category_plan = self.vModel.PaycheckPlan.cCategoryPlans[cell.category]
        category_plan.amount = self.grid_slaves(cell.grid_info()['row'], 1)[0].get()
        category_plan.period = self.grid_slaves(cell.grid_info()['row'], 2)[0].get()
        print(self.vModel.PaycheckPlan.Narrate())
