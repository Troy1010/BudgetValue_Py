import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import BudgetValue as BV  # noqa
from BudgetValue.View import WidgetFactories as WF  # noqa
from . import Misc  # noqa
from .Skin import vSkin
from .Misc import ModelTable
from Model.Misc import List_ValueStream
from Model import CategoryType
from .._Logger import BVLog


class SeparationLable():
    def __init__(self, name):
        self.name = name


class ViewModel_CategoryTable(List_ValueStream):

    def __init__(self, vModel, *args, **kwargs):
        super().__init__()
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        for category_name in vModel.Budgeted.cCategoryTotalStreams.keys():
            self.append(self.vModel.Categories[category_name])
        self.Format()
        # if an item of vModel.Budgeted.cCategoryTotalStreams is created or destroyed, update self

        def OnNewCategoryTotalStreamValueAddPair(self, collection_edit_info):
            if collection_edit_info.bAdd:
                self.append(self.vModel.Categories[collection_edit_info.key])
            else:
                self.remove(self.vModel.Categories[collection_edit_info.key])
            self.Format()
        vModel.Budgeted.cCategoryTotalStreams._value_stream.subscribe(lambda category_name: OnNewCategoryTotalStreamValueAddPair(self, category_name))

    def Format(self):
        # remove all SeparationLabels
        items_to_delete = []
        for item in self:
            if not isinstance(item, BV.Model.Category):
                items_to_delete.append(item)
        for item in items_to_delete:
            self.remove(item)
        # sort
        self.sort(key=lambda item: CategoryType.GetIndex(item.type))
        # add SeparationLabels
        prev_type = None
        i = 0
        for category in list(self):
            if prev_type != category.type:
                self.insert(i, SeparationLable(category.type.name.capitalize()))
                prev_type = category.type
                i += 1
            i += 1


class CategoryTable(ModelTable):
    VM_CategoryTable = None

    def __init__(self, parent, vModel, *args, bNoSeparationLabelText=False, **kwargs):
        super().__init__(parent, vModel, *args, **kwargs)
        self.iFirstDataColumn = 0
        self.iFirstDataRow = 2
        self.bNoSeparationLabelText = bNoSeparationLabelText
        #
        if self.VM_CategoryTable is None:
            self.VM_CategoryTable = ViewModel_CategoryTable(vModel)

    def Refresh(self):
        super().Refresh()
        # Add Separation Labels
        for item in self.VM_CategoryTable:
            if isinstance(item, SeparationLable):
                text = " " if self.bNoSeparationLabelText else "  " + item.name
                WF.MakeSeparationLabel(self, self.GetRowOfValue(item), text)

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
        for category in self.VM_CategoryTable:
            if not isinstance(category, BV.Model.Category):
                continue
            w = tk.Frame(self)
            w.grid(row=self.GetRowOfValue(category), column=self.iFirstDataColumn)
            w.config(height=height)
        #

        def OnCategoryTotalStreamsAddOrRemove(value_add_pair):
            pass
            # if value_add_pair.bAdd:
            #     w = tk.Frame(self)
            #     w.grid(row=self.GetRowOfCategory(value_add_pair.key), column=self.iFirstDataColumn)
            #     w.config(height=height)
            # else:
            #     self.grid_remove(row=1, column=self.iFirstDataColumn)
        self.cDisposables.append(self.vModel.Budgeted.cCategoryTotalStreams._value_stream.subscribe(OnCategoryTotalStreamsAddOrRemove))

        self.iFirstDataColumn += 1

    def GetCategoryOfRow(self, row):
        return self.VM_CategoryTable[(row-self.iFirstDataRow)]

    def GetRowOfValue(self, value):
        if isinstance(value, str):
            value = self.vModel.Categories[value]
        elif isinstance(value, BV.Model.Category) or isinstance(value, BV.View.CategoryTable.SeparationLable):
            pass
        else:
            BVLog.error(TM.FnName()+" recieved invalid value argument:"+str(value))
        try:
            returning = self.iFirstDataRow + list(self.VM_CategoryTable).index(value)
        except ValueError:  # could not find value in VM_CategoryTable
            BVLog.warning(TM.FnName()+" could not find value:"+str(value)+" in VM_CategoryTable")
            returning = None
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
        for category in self.VM_CategoryTable:
            if not isinstance(category, BV.Model.Category):
                continue
            row = self.GetRowOfValue(category.name)
            w = WF.MakeEntry(self, (row, 0), text=category.name, justify=tk.LEFT, bBold=True, bEditableState=False, background=vSkin.BG_ENTRY)

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
