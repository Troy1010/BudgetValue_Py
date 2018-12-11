from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
from BudgetValue.View import Fonts
import TM_CommonPy as TM
import BudgetValue as BV
import decimal
from decimal import Decimal


class TableData(TM.tk.TableFrame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.Refresh()

    def Refresh(self):
        # remove old
        for child in BV.GetAllChildren(self):
            child.grid_forget()
            child.destroy()
        # add new
        for i, category in enumerate(self.vModel.Categories.GetTrueCategories()):
            self.MakeText((i, 0), category)
            try:
                amount = self.vModel.PaycheckPlan[category].amount
            except KeyError:
                amount = None
            self.MakeEntry((i, 1), category, amount)
            try:
                period = self.vModel.PaycheckPlan[category].period
            except KeyError:
                period = None
            cell = self.MakeEntry((i, 2), category, period)
            self.MakeEntry((i, 3), category)
            self.MakeRowValid(i, cell)

    def MakeText(self, cRowColumnPair, category):
        w = tk.Text(self, font=Fonts.FONT_SMALL, width=15, borderwidth=2, height=1, relief='ridge', background='SystemButtonFace')
        w.insert(1.0, category.name)
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])
        w.configure(state="disabled")
        w.category = category

    def MakeEntry(self, cRowColumnPair, category, text=None):
        w = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15, justify=tk.RIGHT,
                        borderwidth=2, relief='ridge', background='SystemButtonFace')
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])
        w.bind("<FocusIn>", lambda event, w=w: self.Entry_FocusIn(event, w))
        w.bind("<FocusOut>", lambda event, w=w: self.Entry_FocusOut(event, w))
        w.bind("<Return>", lambda event, w=w: self.Entry_Return(event, w))
        w.category = category
        w.ValidationHandler = BV.MakeValid_Money
        if text:
            w.text = text
        return w

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
        # Get values of row
        try:
            amount = Decimal(str(self.GetCell(row, 1).text))
        except decimal.InvalidOperation:  # cell was empty
            amount = None
        try:
            period = Decimal(str(self.GetCell(row, 2).text))
        except decimal.InvalidOperation:  # cell was empty
            period = None
        try:
            plan = Decimal(str(self.GetCell(row, 3).text))
        except decimal.InvalidOperation:  # cell was empty
            plan = None
        # if we can complete the row, do so.
        if cellThatChanged.column != 3 and amount and period:
            try:
                self.GetCell(row, 3).text = amount / period
            except ValueError:
                pass
        elif cellThatChanged.column != 2 and amount and plan:
            try:
                self.GetCell(row, 2).text = amount / plan
            except ValueError:
                pass
        elif cellThatChanged.column != 1 and period and plan:
            try:
                self.GetCell(row, 1).text = plan * period
            except ValueError:
                pass

    def SaveCategoryPlan(self, row):
        category = self.GetCell(row, 0).category
        if category not in self.vModel.PaycheckPlan:
            self.vModel.PaycheckPlan[category] = self.vModel.PaycheckPlan.CategoryPlan()
        category_plan = self.vModel.PaycheckPlan[category]
        category_plan.amount = self.grid_slaves(row, 1)[0].get()
        category_plan.period = self.grid_slaves(row, 2)[0].get()
        if category_plan.IsEmpty():
            del self.vModel.PaycheckPlan[category]
