import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import rx  # noqa
from .Skin import vSkin  # noqa
import BudgetValue as BV
from . import WidgetFactories as WF


class ModelTable(TM.tk.TableFrame):
    iFirstDataColumn = 0
    iFirstDataRow = 1

    def __init__(self, parent, vModel):
        super().__init__(parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.parent = parent
        self.cDisposables = []

    def Refresh(self):
        # remove old
        for child in self.winfo_children():
            try:
                if not child.bPerminent:
                    child.grid_forget()
                    child.destroy()
            except AttributeError:
                child.grid_forget()
                child.destroy()
        if hasattr(self, 'cDisposables'):
            for disposable in self.cDisposables:
                disposable.dispose()
        self.cDisposables = []


class CategoryTable(ModelTable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iFirstDataColumn = 0
        self.iFirstDataRow = 1

    def FinishRefresh(self):
        self.AddSeparationLables()

    def AddSpacersForBudgeted(self):
        row = self.iFirstDataRow
        # Get height
        # fix: There must be a better way..
        height_widget = WF.MakeEntry_ReadOnly(self, (row, self.iFirstDataColumn), text="z", validation=BV.MakeValid_Money, display=BV.MakeValid_Money_ZeroIsNone)
        height_widget.update_idletasks()
        height = height_widget.winfo_height()
        height_widget.grid_forget()
        height_widget.destroy()
        # Data
        for category in self.vModel.Categories.Select():
            # Budgeted
            if category.name in self.vModel.Budgeted.cCategoryTotalStreams:
                w = tk.Frame(self)
                w.grid(row=row, column=self.iFirstDataColumn)
                w.config(height=height)
            row += 1
        #
        self.iFirstDataColumn += 1

    def AddSeparationLables(self, no_text=False):
        prev_type = None
        row = self.GetMaxRow()
        while row >= self.iFirstDataRow:
            category = self.GetCategoryOfRow(row)
            if category is None or self.IsRowEmpty(row):
                row -= 1
                continue
            if prev_type != category.type:
                if prev_type is None:
                    row -= 1
                    prev_type = category.type
                    continue
                self.InsertRow(row+1)
                if no_text:
                    WF.MakeSeparationLable(self, row+1, " ")
                else:
                    WF.MakeSeparationLable(self, row+1, "  " + prev_type.name.capitalize())
                prev_type = category.type
            row -= 1
        self.InsertRow(row+1)
        if no_text:
            WF.MakeSeparationLable(self, row+1, " ")
        else:
            WF.MakeSeparationLable(self, row+1, "  " + prev_type.name.capitalize())

    def GetCategoryOfRow(self, row):
        # Only works before SeparationLables are added
        # fix: There must be a better way..
        for i, category in enumerate(self.vModel.Categories.values()):
            if i == row - self.iFirstDataRow:
                return category
        return None

    def AddRowHeaderColumn(self):
        w = WF.MakeHeader(self, (0, 0), text="Category")

        def ShowCategoryColHeaderMenu(event):
            vDropdown = tk.Menu(tearoff=False)
            vDropdown.add_command(label="Add Category", command=lambda x=event.x_root-self.winfo_toplevel().winfo_rootx(), y=event.y_root-self.winfo_toplevel().winfo_rooty(): (
                BV.View.Popup_AddCategory(self.winfo_toplevel(),
                                          lambda text: self.vModel.Categories.AddCategory(text),
                                          cPos=(x, y)
                                          )
            ))
            vDropdown.post(event.x_root, event.y_root)
        w.bind("<Button-3>", lambda event: ShowCategoryColHeaderMenu(event), add="+")
        for row, category in enumerate(self.vModel.Categories.Select()):
            if not self.IsRowEmpty(row+self.iFirstDataRow):
                w = WF.MakeEntry(self, (row+self.iFirstDataRow, 0), text=category.name, justify=tk.LEFT, bBold=True, bEditableState=False, background=vSkin.BG_ENTRY)

                def AssignCategoryType(category_type_name, category):
                    category.type = BV.Model.CategoryType.GetByName(category_type_name)
                    self.Refresh()

                def ShowCategoryCellMenu(event):
                    vDropdown = tk.Menu(tearoff=False)
                    vDropdown.add_command(label="Remove Category", command=lambda category=category: self.vModel.Categories.RemoveCategory(category.name))  # fix: refreshes improperly
                    vDropdown.add_command(label="Assign Type", command=lambda x=event.x_root-self.winfo_toplevel().winfo_rootx(), y=event.y_root-self.winfo_toplevel().winfo_rooty(): (
                        BV.View.Popup_SelectCategoryType(self.winfo_toplevel(),
                                                         lambda category_type_name, category=category: AssignCategoryType(category_type_name, category),
                                                         cPos=(x, y)
                                                         )
                    ))
                    vDropdown.post(event.x_root, event.y_root)
                w.bind("<Button-3>", lambda event: ShowCategoryCellMenu(event), add="+")
