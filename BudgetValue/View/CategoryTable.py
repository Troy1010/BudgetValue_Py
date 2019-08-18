import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import BudgetValue as BV  # noqa
from BudgetValue.View import WidgetFactories as WF  # noqa
from . import Misc  # noqa
from .Skin import vSkin
from .Misc import ModelTable
from Model.DataTypes import List_ValueStream
from Model import CategoryType
from .._Logger import BVLog
from .._Logger import Log


class SeparationLable():
    def __init__(self, type_):
        self.type = type_
        self.name = type_.name


class ViewModel_CategoryTable(List_ValueStream):
    count = 0

    def __init__(self, vModel, *args, **kwargs):
        assert ViewModel_CategoryTable.count <= 1  # ViewModel_CategoryTable should be a singleton
        ViewModel_CategoryTable.count += 1
        super().__init__()
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        # SeparationLabels M -> VM

        def AddOrRemoveSeparationLabels(edit_info):
            if edit_info.bAdd:
                # If I am a new type, insert my SeparationLabel
                if edit_info.value.type not in [(x.type if edit_info.value != x else None) for x in self]:
                    self.SortedInsert(SeparationLable(edit_info.value.type))
            else:
                # If I was the last of my category, remove my SeparationLabel
                for item in self:
                    if edit_info.value == item or isinstance(item, SeparationLable):
                        continue
                    if edit_info.value.type == item.type:
                        break
                else:
                    assert self[self.index(edit_info.value) - 1].name.lower() == edit_info.value.type.name.lower()
                    del self[self.index(edit_info.value) - 1]
        self._value_stream.subscribe(AddOrRemoveSeparationLabels)
        # bring in current values from vModel.Budgeted.cCategoryTotalStreams
        for category_name in vModel.Budgeted.cCategoryTotalStreams.keys():
            self.SortedInsert(self.vModel.Categories[category_name])
        # stream in values from vModel.Budgeted.cCategoryTotalStreams

        def OnNewCategoryTotalStreamValue(self, collection_edit_info):
            category_added_or_removed = self.vModel.Categories[collection_edit_info.key]
            if collection_edit_info.bAdd:
                self.SortedInsert(category_added_or_removed)
            else:
                self.remove(category_added_or_removed)
        vModel.Budgeted.cCategoryTotalStreams._value_stream.subscribe(lambda category_name: OnNewCategoryTotalStreamValue(self, category_name))

    def get_sort_key(self, value):
        type_index = CategoryType.GetIndex(value.type)
        bSeparationLabel = not isinstance(value, SeparationLable)
        return (type_index, bSeparationLabel, value.name)

    def GetInsertionIndex(self, value):
        sort_tuple = self.get_sort_key(value)
        for i, item in enumerate(self):
            if sort_tuple < self.get_sort_key(item):
                return i
        return -1

    def SortedInsert(self, value):
        # determine insertion_index
        insertion_index = self.GetInsertionIndex(value)
        # insert at insertion_index
        if insertion_index == -1:
            self.append(value)
        else:
            self.insert(insertion_index, value)


class CategoryTable(ModelTable):
    VM_CategoryTable = None

    def __init__(self, parent, vModel, *args, bNoSeparationLabelText=False, bAddSpacers=False, bAddCategoryRowHeaderColumn=True, bAddBudgetedColumn=True, **kwargs):
        super().__init__(parent, vModel, *args, **kwargs)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.iFirstDataColumn = 0
        if bAddSpacers:
            self.iSpacerColumn = self.iFirstDataColumn
            self.iFirstDataColumn += 1
        if bAddCategoryRowHeaderColumn:
            self.iCategoryRowHeaderColumn = self.iFirstDataColumn
            self.iFirstDataColumn += 1
        if bAddBudgetedColumn:
            self.iBudgetedColumn = self.iFirstDataColumn
            self.iFirstDataColumn += 1
        self.iFirstDataRow = 2
        self.bNoSeparationLabelText = bNoSeparationLabelText
        self.bAddSpacers = bAddSpacers
        self.bAddCategoryRowHeaderColumn = bAddCategoryRowHeaderColumn
        self.bAddBudgetedColumn = bAddBudgetedColumn
        # instantiate ViewModel_CategoryTable
        if CategoryTable.VM_CategoryTable is None:
            CategoryTable.VM_CategoryTable = ViewModel_CategoryTable(vModel)
        # Determine spacer_height
        # fix: There must be a better way to determine the right spacer height..
        assert self.GetCell(self.iFirstDataRow, self.iFirstDataColumn) is None
        spacer_height_widget = WF.MakeEntry_ReadOnly(self, (self.iFirstDataRow, self.iFirstDataColumn), text="z")
        spacer_height_widget.update_idletasks()
        self.spacer_height = spacer_height_widget.winfo_height()
        spacer_height_widget.grid_forget()
        spacer_height_widget.destroy()
        # Link M/VM -> V

        def VM_to_V(collection_edit):
            row = self.GetRowOfVMValue(collection_edit.value)
            if collection_edit.bAdd:
                self.InsertRow(row)
                if isinstance(collection_edit.value, SeparationLable):
                    # Separation Labels
                    text = " " if self.bNoSeparationLabelText else "  " + collection_edit.value.type.name.capitalize()
                    WF.MakeSeparationLabel(self, row, text)
                elif isinstance(collection_edit.value, BV.Model.Category):
                    # Spacers
                    if bAddSpacers:
                        w = tk.Frame(self)
                        w.grid(row=self.GetRowOfVMValue(collection_edit.value), column=self.iSpacerColumn)
                        w.config(height=self.spacer_height)
                    # CategoryRowHeader
                    if bAddCategoryRowHeaderColumn:
                        self.MakeCategoryRowHeader(collection_edit.value)
            else:
                self.UninsertRow(row)
        self.VM_CategoryTable._value_stream.subscribe(VM_to_V)

        def M_to_V(collection_edit):
            if collection_edit.bAdd:
                if collection_edit.key in self.vModel.Categories:
                    # Budgeted
                    if bAddBudgetedColumn:
                        self.MakeBudgetedEntry(self.vModel.Categories[collection_edit.key])

        self.vModel.Budgeted.cCategoryTotalStreams._value_stream.subscribe(M_to_V)
        #
        self.Refresh()

    def Refresh(self):
        super().Refresh()
        # Refresh Separation Labels
        for item in self.VM_CategoryTable:
            if isinstance(item, SeparationLable):
                text = " " if self.bNoSeparationLabelText else "  " + item.type.name.capitalize()
                WF.MakeSeparationLabel(self, self.GetRowOfVMValue(item), text)
        # Refresh Spacers
        if self.bAddSpacers:
            for item in self.VM_CategoryTable:
                if isinstance(item, BV.Model.Category):
                    w = tk.Frame(self)
                    w.grid(row=self.GetRowOfVMValue(item), column=self.iSpacerColumn)
                    w.config(height=self.spacer_height)
        # Refresh Category Column
        if self.bAddCategoryRowHeaderColumn:
            self.MakeCategorysColumnHeader()
            for item in self.VM_CategoryTable:
                if isinstance(item, BV.Model.Category):
                    self.MakeCategoryRowHeader(item)
        # Refresh Budgeted Column
        if self.bAddBudgetedColumn:
            WF.MakeHeader(self, (0, self.iBudgetedColumn), text="Budgeted", background=vSkin.BG_BUDGETED)
            for category in self.VM_CategoryTable:
                if isinstance(category, BV.Model.Category):
                    self.MakeBudgetedEntry(category)
            row = self.GetMaxRow() + self.iFirstDataRow
            # Black bar
            tk.Frame(self, background='black', height=2).grid(row=row, columnspan=self.GetMaxColumn()+1, sticky="ew")
            row += 1
            # Budgeted Total
            if self.iBudgetedColumn > 0:
                WF.MakeLable(self, (row, self.iBudgetedColumn-1), text="Total", width=WF.Buffer(1))
            WF.MakeEntry(self, (row, self.iBudgetedColumn), text=self.vModel.Budgeted.total_stream, justify=tk.CENTER, bEditableState=False, background=vSkin.BG_ENTRY, display=BV.MakeValid_Money)

    def MakeBudgetedEntry(self, category):
        assert isinstance(category, BV.Model.Category)
        w = WF.MakeEntry_ReadOnly(self, (self.GetRowOfVMValue(category.name), self.iBudgetedColumn), text=self.vModel.Budgeted.cCategoryTotalStreams[category.name], validation=BV.MakeValid_Money, display=BV.MakeValid_Money_ZeroIsNone)

        def HighlightBudgeted(budgeted_amount, w):
            if budgeted_amount < 0:
                w.configure(readonlybackground=vSkin.BG_BUDGETED_BAD)
            else:
                w.configure(readonlybackground=vSkin.BG_BUDGETED)
        disposable = self.vModel.Budgeted.cCategoryTotalStreams[category.name].subscribe(
            lambda budgeted_amount, w=w: HighlightBudgeted(budgeted_amount, w)
        )
        self.cDisposables.append(disposable)

    def MakeCategorysColumnHeader(self):
        w = WF.MakeHeader(self, (0, self.iCategoryRowHeaderColumn), text="Category")

        def ShowCategoryColHeaderMenu(event):
            vDropdown = tk.Menu(tearoff=False)
            vDropdown.add_command(label="Create New Category", command=lambda x=event.x_root-self.winfo_toplevel().winfo_rootx(), y=event.y_root-self.winfo_toplevel().winfo_rooty(): (
                BV.View.Popup_InputText(self.winfo_toplevel(),
                                        lambda text: self.vModel.Categories.AddCategory(text),
                                        cPos=(x, y),
                                        sPrompt="Input category name:"
                                        )
            ))

            vDropdown.add_command(label="Remove Category", command=lambda x=event.x_root-self.winfo_toplevel().winfo_rootx(), y=event.y_root-self.winfo_toplevel().winfo_rooty(): (
                BV.View.Popup_SelectFromList(self.winfo_toplevel(),
                                             self.vModel.Categories.RemoveCategory,
                                             [category_name for category_name in self.vModel.Categories],
                                             cPos=(x, y)
                                             )
            ))
            vDropdown.post(event.x_root, event.y_root)
        w.bind("<Button-3>", lambda event: ShowCategoryColHeaderMenu(event), add="+")

    def MakeCategoryRowHeader(self, category):
        assert isinstance(category, BV.Model.Category)
        row = self.GetRowOfVMValue(category.name)
        w = WF.MakeEntry(self, (row, self.iCategoryRowHeaderColumn), text=category.name, justify=tk.LEFT, bBold=True, bEditableState=False, background=vSkin.BG_ENTRY)

        def AssignCategoryType(category_type_name, category_):
            category_.type = BV.Model.CategoryType.GetByName(category_type_name)

        def ShowCategoryCellMenu(event, category_):
            vDropdown = tk.Menu(tearoff=False)
            vDropdown.add_command(label="Remove Category", command=lambda category=category_: self.vModel.Categories.RemoveCategory(category_.name))
            vDropdown.add_command(label="Assign Category Type", command=lambda category=category_, x=event.x_root-self.winfo_toplevel().winfo_rootx(), y=event.y_root-self.winfo_toplevel().winfo_rooty(): (
                BV.View.Popup_SelectFromList(self.winfo_toplevel(),
                                             lambda category_type_name: AssignCategoryType(category_type_name, category_),
                                             [x.name.capitalize() for x in BV.Model.CategoryType],
                                             cPos=(x, y)
                                             )
            ))
            vDropdown.post(event.x_root, event.y_root)
        w.bind("<Button-3>", lambda event, category=category: ShowCategoryCellMenu(event, category), add="+")

    def GetCategoryOfRow(self, row):
        return self.VM_CategoryTable[(row-self.iFirstDataRow)]

    def GetRowOfVMValue(self, value):
        if isinstance(value, str):
            value = self.vModel.Categories[value]
        elif isinstance(value, BV.Model.Category) or isinstance(value, BV.View.CategoryTable.SeparationLable):
            pass
        else:
            BVLog.error(TM.FnName()+" recieved invalid value argument:"+str(value))
        try:
            returning = self.iFirstDataRow + list(self.VM_CategoryTable).index(value)
        except ValueError:  # could not find value in VM_CategoryTable
            BVLog.debug(TM.FnName()+" could not find value:"+str(value)+" by name:"+("<NoName>" if not hasattr(value, 'name') else value.name)+" in VM_CategoryTable.")
            returning = None
        Log(TM.FnName()+". value:"+str(value)+" value_name:" + ("<NoName>" if not hasattr(value, 'name') else value.name)+" row:"+str(returning))
        return returning
