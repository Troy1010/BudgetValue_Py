from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
from BudgetValue.View import Fonts
import BudgetValue as BV


class PaycheckPlan(tk.Frame):
    name = "Paycheck Plan"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel

        for i, category in enumerate(vModel.Categories.GetTrueCategories()):
            self.MakeText((i, 0), category)
            self.MakeEntry((i, 1), category)
            self.MakeEntry((i, 2), category)
            self.MakeEntry((i, 3), category)

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
        w.bind("<Return>", lambda event, w=w: self.Entry_Return(event, w))
        w.category = category

    def SetEntry(self, entry, value):
        entry.delete(0, tk.END)
        if value:
            if value.is_integer():
                value = int(value)
            entry.insert(0, value)

    def Entry_FocusIn(self, event, cell):
        cell.config(justify=tk.LEFT)
        BV.select_all(cell)

    def Entry_FocusOut(self, event, cell):
        cell.config(justify=tk.RIGHT)
        self.SaveCategoryPlan(cell)
        amountPerWeek = None
        if cell.category in self.vModel.PaycheckPlan.cCategoryPlans:
            amountPerWeek = self.vModel.PaycheckPlan.cCategoryPlans[cell.category].amountPerWeek
        self.SetEntry(self.grid_slaves(cell.grid_info()['row'], 3)[0], amountPerWeek)

    def Entry_Return(self, event, cell):
        list_of_cell_to_the_right = self.grid_slaves(cell.grid_info()['row'], cell.grid_info()['column'] + 1)
        if list_of_cell_to_the_right:
            list_of_cell_to_the_right[0].focus_set()
            return
        list_of_first_entry_in_next_row = self.grid_slaves(cell.grid_info()['row'] + 1, 1)
        if list_of_first_entry_in_next_row:
            list_of_first_entry_in_next_row[0].focus_set()
            return
        cell.winfo_toplevel().focus_set()

    def SaveCategoryPlan(self, cell):
        if cell.category not in self.vModel.PaycheckPlan.cCategoryPlans:
            self.vModel.PaycheckPlan.cCategoryPlans[cell.category] = self.vModel.PaycheckPlan.CategoryPlan()
        category_plan = self.vModel.PaycheckPlan.cCategoryPlans[cell.category]
        category_plan.amount = self.grid_slaves(cell.grid_info()['row'], 1)[0].get()
        category_plan.period = self.grid_slaves(cell.grid_info()['row'], 2)[0].get()
        if category_plan.IsEmpty():
            del self.vModel.PaycheckPlan.cCategoryPlans[cell.category]
