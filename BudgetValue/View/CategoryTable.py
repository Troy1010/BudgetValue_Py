import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import BudgetValue as BV  # noqa
from BudgetValue.View import WidgetFactories as WF  # noqa
from . import Misc  # noqa
from .Skin import vSkin
from .Misc import ModelTable


class CategoryTable(ModelTable):

    def __init__(self, parent, vModel, *args, **kwargs):
        super().__init__(parent, vModel, *args, **kwargs)
        self.iFirstDataColumn = 0
        self.iFirstDataRow = 2

    def Refresh(self):
        super().Refresh()

    def FinishRefresh(self):
        self.AddSeparationLables()

    def AddSpacersForBudgeted(self):
        row = self.iFirstDataRow
        # Determine height
        # fix: There must be a better way to determine the right height..
        height_widget = WF.MakeEntry_ReadOnly(self, (row, self.iFirstDataColumn), text="z", validation=BV.MakeValid_Money, display=BV.MakeValid_Money_ZeroIsNone)
        height_widget.update_idletasks()
        height = height_widget.winfo_height()
        height_widget.grid_forget()
        height_widget.destroy()
        # Data
        for category_name in self.vModel.Budgeted.cCategoryTotalStreams.keys():
            w = tk.Frame(self)
            w.grid(row=self.GetRowOfCategory(category_name), column=self.iFirstDataColumn)
            w.config(height=height)
        #

        def OnCategoryTotalStreamsAddOrRemove(value_add_pair):
            if value_add_pair.bAdd:
                w = tk.Frame(self)
                w.grid(row=1, column=self.iFirstDataColumn)
                w.config(height=height)
            else:
                self.grid_remove(row=1, column=self.iFirstDataColumn)
        self.cDisposables.append(self.vModel.Budgeted.cCategoryTotalStreams._value_stream.subscribe(OnCategoryTotalStreamsAddOrRemove))

        self.iFirstDataColumn += 1

    def AddSeparationLables(self, no_text=False):
        return
        row = self.iFirstDataRow
        prev_type = None
        for category in self.vModel.Categories.values():
            if prev_type != category.type:
                if no_text:
                    WF.MakeSeparationLable(self, row+1, " ")
                else:
                    WF.MakeSeparationLable(self, row+1, "  " + category.type.name.capitalize())
                prev_type = category.type
            row += 2

        return
        prev_type = None
        row = self.GetMaxRow()
        while row >= self.iFirstDataRow:
            category = self.GetCategoryOfRow(row)
            if category is None or self.IsRowEmpty(row):
                row -= 2
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
            row -= 2
        self.InsertRow(row+1)
        if no_text:
            WF.MakeSeparationLable(self, row+1, " ")
        else:
            if hasattr(prev_type, 'name'):
                WF.MakeSeparationLable(self, row+1, "  " + prev_type.name.capitalize())
            else:
                WF.MakeSeparationLable(self, row+1, "  None")

    def GetCategoryOfRow(self, row):
        dv = list(self.vModel.Categories.values())
        dv[(row-self.iFirstDataRow)/2]
        return self.vModel.Categories.values()[(row-self.iFirstDataRow)/2]

    def GetRowOfCategory(self, category):
        if isinstance(category, BV.Model.Category):
            category = category.name
        returning = self.iFirstDataRow + list(self.vModel.Categories.keys()).index(category)*2
        return returning

    def AddRowHeaderColumn(self):
        # ColumnHeader
        w = WF.MakeHeader(self, (0, 0), text="Category")

        def ShowCategoryColHeaderMenu(event):
            vDropdown = tk.Menu(tearoff=False)
            vDropdown.add_command(label="Create New Category", command=lambda x=event.x_root-self.winfo_toplevel().winfo_rootx(), y=event.y_root-self.winfo_toplevel().winfo_rooty(): (
                BV.View.Popup_InputText(self.winfo_toplevel(),
                                        lambda text: self.vModel.Categories.AddCategory(text),
                                        cPos=(x, y),
                                        sPrompt="Input category name:"
                                        )
            ))

            def RemoveCategory(category):  # fix: I should rx this
                self.vModel.Categories.RemoveCategory(category)
                if hasattr(self, "RefreshParent"):
                    self.RefreshParent()
                else:
                    self.Refresh()
            vDropdown.add_command(label="Remove Category", command=lambda x=event.x_root-self.winfo_toplevel().winfo_rootx(), y=event.y_root-self.winfo_toplevel().winfo_rooty(): (
                BV.View.Popup_SelectFromList(self.winfo_toplevel(),
                                             RemoveCategory,
                                             [category_name for category_name in self.vModel.Categories],
                                             cPos=(x, y)
                                             )
            ))
            vDropdown.post(event.x_root, event.y_root)
        w.bind("<Button-3>", lambda event: ShowCategoryColHeaderMenu(event), add="+")
        # RowHeaders
        for category_name in self.vModel.Budgeted.cCategoryTotalStreams.keys():
            category = self.vModel.Categories[category_name]
            row = self.GetRowOfCategory(category_name)
            w = WF.MakeEntry(self, (row, 0), text=category_name, justify=tk.LEFT, bBold=True, bEditableState=False, background=vSkin.BG_ENTRY)

            def AssignCategoryType(category_type_name, category_):
                category_.type = BV.Model.CategoryType.GetByName(category_type_name)
                if hasattr(self, "RefreshParent"):
                    self.RefreshParent()
                else:
                    self.Refresh()

            def RemoveCategory(category_name):  # fix: I should rx this
                self.vModel.Categories.RemoveCategory(category_name)
                if hasattr(self, "RefreshParent"):
                    self.RefreshParent()
                else:
                    self.Refresh()

            def ShowCategoryCellMenu(event, category_):
                vDropdown = tk.Menu(tearoff=False)
                vDropdown.add_command(label="Remove Category", command=lambda category=category_: RemoveCategory(category_.name))
                vDropdown.add_command(label="Assign Category Type", command=lambda category=category_, x=event.x_root-self.winfo_toplevel().winfo_rootx(), y=event.y_root-self.winfo_toplevel().winfo_rooty(): (
                    BV.View.Popup_SelectFromList(self.winfo_toplevel(),
                                                 lambda category_type_name: AssignCategoryType(category_type_name, category_),
                                                 [x.name.capitalize() for x in BV.Model.CategoryType],
                                                 cPos=(x, y)
                                                 )
                ))
                vDropdown.post(event.x_root, event.y_root)
            w.bind("<Button-3>", lambda event, category=category: ShowCategoryCellMenu(event, category), add="+")
