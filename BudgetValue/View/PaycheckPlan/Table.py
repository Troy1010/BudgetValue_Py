from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
from BudgetValue.View import Fonts
import TM_CommonPy as TM
import BudgetValue as BV
from decimal import Decimal
from BudgetValue.Model import CategoryType  # noqa


class Table(TM.tk.TableFrame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.parent = parent

    def Refresh(self):
        # remove old
        for child in BV.GetAllChildren(self):
            child.grid_forget()
            child.destroy()
        # add new
        row = 0
        # Header
        for j, header_name in enumerate(['Category', 'Amount', 'Period', 'Plan']):
            self.MakeHeader((row, j), text=header_name)
        row += 1
        # Data
        prev_type = None
        for category in self.vModel.Categories.Select(types_exclude=[CategoryType.extra]):
            # make separation label if needed
            if prev_type != category.type:
                prev_type = category.type
                self.MakeSeparationLable(row, "  " + prev_type.name.capitalize())
                row += 1
            # generate row
            amount = None if category not in self.vModel.PaycheckPlan else self.vModel.PaycheckPlan[category].amount
            period = None if category not in self.vModel.PaycheckPlan else self.vModel.PaycheckPlan[category].period
            if category.IsSpendable():
                self.MakeText((row, 0), category, text=category.name)
                self.MakeEntry((row, 1), category)
                self.MakeEntry((row, 2), category, text=period)
                self.MakeEntry((row, 3), category, text=amount)
                self.MakeRowValid(row)
            else:
                self.MakeText((row, 0), category, text=category.name, columnspan=3)
                self.MakeEntry((row, 3), category, text=amount)
            row += 1
        # Balance
        tk.Frame(self, background='black', height=2).grid(row=row, columnspan=4, sticky="ew")
        row += 1
        vBalance = tk.Label(self, font=Fonts.FONT_LARGE, borderwidth=2, width=15, height=1,
                            relief='ridge', background='SystemButtonFace', text="Balance")
        vBalance.grid(row=row, column=0, columnspan=3, sticky="ewn")
        self.vBalanceNum = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15,
                                       borderwidth=2, relief='ridge', justify='center', state="readonly")
        self.vBalanceNum.grid(row=row, column=3, sticky="ewns")
        row += 1
        #
        self.excessDumpCell = self.GetCell(row-3, 3)
        self.DistributeBalance()
        self.CalcAndShowBalance()

    def DistributeBalance(self, cellToKeep=None):
        if cellToKeep != self.excessDumpCell:
            dBalance = self.CalculateBalance()
            self.excessDumpCell.text = Decimal(self.excessDumpCell.text) + dBalance
            self.SaveToModel(self.excessDumpCell.row)

    def CalcAndShowBalance(self):
        dBalance = self.CalculateBalance()
        self.vBalanceNum.text = str(dBalance)
        # color
        if dBalance != 0:
            self.vBalanceNum.config(readonlybackground="pink")
        else:
            self.vBalanceNum.config(readonlybackground="lightgreen")

    def CalculateBalance(self):
        dBalance = 0
        for category_plan in self.vModel.PaycheckPlan.values():
            if category_plan.amount is None:
                continue
            if category_plan.category.type == CategoryType.income:
                dBalance += category_plan.amount
            else:
                dBalance -= category_plan.amount
        return dBalance

    def MakeHeader(self, cRowColumnPair, text=None):
        w = tk.Label(self, font=Fonts.FONT_SMALL_BOLD, borderwidth=2, width=15, height=1, relief='ridge',
                     background='SystemButtonFace', text=text)
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])

    def MakeSeparationLable(self, row, text):
        w = tk.Label(self, font=Fonts.FONT_SMALL_BOLD, width=15, borderwidth=2, height=1, relief=tk.FLAT,
                     background='lightblue', text=text, anchor="w")
        w.grid(row=row, columnspan=4, sticky="ew")

    def MakeText(self, cRowColumnPair, category, text=None, columnspan=1):
        w = tk.Text(self, font=Fonts.FONT_SMALL, width=15, height=1,
                    borderwidth=2, relief='ridge', background='SystemButtonFace')
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan, sticky="ew")
        w.category = category
        if text:
            w.insert(1.0, text)
        w.configure(state="disabled")

    def MakeEntry(self, cRowColumnPair, category, text=None, columnspan=1):
        w = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15, justify=tk.RIGHT,
                        borderwidth=2, relief='ridge', background='SystemButtonFace')
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan)
        w.bind("<FocusIn>", lambda event, w=w: self.Entry_FocusIn(w))
        w.bind("<FocusOut>", lambda event, w=w: self.Entry_FocusOut(w))
        w.bind("<Return>", lambda event, w=w: self.Entry_Return(w))
        w.category = category
        w.ValidationHandler = BV.MakeValid_Money
        w.text = text

    def Entry_FocusIn(self, cell):
        cell.config(justify=tk.LEFT)
        cell.select_text()
        cell.text_at_focus_in = cell.text

    def Entry_FocusOut(self, cell):
        cell.config(justify=tk.RIGHT)
        if cell.text_at_focus_in != cell.text:
            cell.MakeValid()
            self.MakeRowValid(cell.row, cellToKeep=cell)
        self.SaveToModel(cell.row)
        self.DistributeBalance(cell)
        self.CalcAndShowBalance()

    def Entry_Return(self, cell):
        list_of_cell_to_the_right = self.grid_slaves(cell.grid_info()['row'], cell.grid_info()['column'] + 1)
        if list_of_cell_to_the_right:
            list_of_cell_to_the_right[0].focus_set()
            return
        list_of_first_entry_in_next_row = self.grid_slaves(cell.grid_info()['row'] + 1, 1)
        if list_of_first_entry_in_next_row:
            list_of_first_entry_in_next_row[0].focus_set()
            return
        cell.winfo_toplevel().focus_set()

    def MakeRowValid(self, row, cellToKeep=None):
        columnToKeep = -1 if cellToKeep is None else cellToKeep.column
        if self.GetCategoryOfRow(row).IsSpendable():
            # Get values of row
            amount = None if not self.GetCell(row, 1).text else Decimal(str(self.GetCell(row, 1).text))
            period = None if not self.GetCell(row, 2).text else Decimal(str(self.GetCell(row, 2).text))
            plan = None if not self.GetCell(row, 3).text else Decimal(str(self.GetCell(row, 3).text))
            # if we can complete the row, do so.
            if columnToKeep != 3 and amount and period:
                self.GetCell(row, 3).text = amount / period
            elif columnToKeep != 2 and amount and plan:
                self.GetCell(row, 2).text = amount / plan
            elif columnToKeep != 1 and period and plan:
                self.GetCell(row, 1).text = plan * period

    def SaveToModel(self, row):
        # Get category
        category = self.GetCategoryOfRow(row)
        # Make a category_plan out of the view's data
        category_plan = self.vModel.PaycheckPlan.CategoryPlan(category)
        if category.IsSpendable():
            category_plan.amount = self.GetCell(row, 3).text
            category_plan.period = self.GetCell(row, 2).text
        else:
            category_plan.amount = self.GetCell(row, 3).text
        # Add category_plan to model
        if category_plan.IsEmpty():
            if category in self.vModel.PaycheckPlan:
                del self.vModel.PaycheckPlan[category]
        else:
            self.vModel.PaycheckPlan[category] = category_plan

    def GetCategoryOfRow(self, row):
        return self.GetCell(row, 0).category
