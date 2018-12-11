from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
from BudgetValue.View import Fonts
import TM_CommonPy as TM
import BudgetValue as BV


class TableData(TM.tk.TableFrame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel

        for i, category in enumerate(vModel.Categories.GetTrueCategories()):
            self.MakeText((i, 0), category)
            self.MakeEntry((i, 1), category)
            self.MakeEntry((i, 2), category)
            self.MakeEntry((i, 3), category)

    def MakeText(self, cRowColumnPair, category):
        w = tk.Text(self, font=Fonts.FONT_SMALL, width=15, borderwidth=2, height=1, relief='ridge', background='SystemButtonFace')
        w.insert(1.0, category.name)
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])
        w.configure(state="disabled")
        w.category = category

    def MakeEntry(self, cRowColumnPair, category):
        w = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15, justify=tk.RIGHT,
                        borderwidth=2, relief='ridge', background='SystemButtonFace')
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])
        w.bind("<FocusIn>", lambda event, w=w: self.Entry_FocusIn(event, w))
        w.bind("<FocusOut>", lambda event, w=w: self.Entry_FocusOut(event, w))
        w.bind("<Return>", lambda event, w=w: self.Entry_Return(event, w))
        w.category = category
        w.ValidationHandler = BV.MakeValid_Money

    def Entry_FocusIn(self, event, cell):
        cell.config(justify=tk.LEFT)
        cell.select_text()
        cell.text_at_focus_in = cell.text

    def Entry_FocusOut(self, event, cell):
        cell.config(justify=tk.RIGHT)
        if cell.text_at_focus_in != cell.text:
            cell.MakeValid()
            self.MakeRowValid(cell.row, cell)
        self.SaveCategoryPlan(cell.row)

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

    def MakeRowValid(self, row, cellThatChanged):
        if not cellThatChanged.text:
            return
        amount = self.GetCell(row, 1).text
        period = self.GetCell(row, 2).text
        amountPerWeek = self.GetCell(row, 3).text
        if cellThatChanged.column == 1:
            try:
                self.GetCell(row, 3).text = float(amount) / float(period)
            except ValueError:
                pass
        elif cellThatChanged.column == 2:
            if self.GetCell(row, 1).text:
                try:
                    self.GetCell(row, 3).text = float(amount) / float(period)
                except ValueError:
                    pass
            else:
                try:
                    self.GetCell(row, 1).text = float(amountPerWeek) * float(period)
                except ValueError:
                    pass
        elif cellThatChanged.column == 3:
            try:
                self.GetCell(row, 2).text = float(amount) / float(amountPerWeek)
            except ValueError:
                pass

    def SaveCategoryPlan(self, row):
        category = self.GetCell(row, 0).category
        if category not in self.vModel.PaycheckPlan.cCategoryPlans:
            self.vModel.PaycheckPlan.cCategoryPlans[category] = self.vModel.PaycheckPlan.CategoryPlan()
        category_plan = self.vModel.PaycheckPlan.cCategoryPlans[category]
        category_plan.amount = self.grid_slaves(row, 1)[0].get()
        category_plan.period = self.grid_slaves(row, 2)[0].get()
        if category_plan.IsEmpty():
            del self.vModel.PaycheckPlan.cCategoryPlans[category]
