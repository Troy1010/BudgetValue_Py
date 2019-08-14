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
        # stream SeparationLabels

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

    def SortedInsert(self, value):
        # determine insertion_index
        sort_tuple = self.get_sort_key(value)
        for i, item in enumerate(self):
            if sort_tuple < self.get_sort_key(item):
                insertion_index = i
                break
        else:
            insertion_index = -1
        # insert at insertion_index
        if insertion_index == -1:
            self.append(value)
        else:
            self.insert(insertion_index, value)


class CategoryTable(ModelTable):
    VM_CategoryTable = None

    def __init__(self, parent, vModel, *args, bNoSeparationLabelText=False, **kwargs):
        super().__init__(parent, vModel, *args, **kwargs)
        self.iFirstDataColumn = 0
        self.iFirstDataRow = 2
        self.bNoSeparationLabelText = bNoSeparationLabelText
        # instantiate ViewModel_CategoryTable
        if CategoryTable.VM_CategoryTable is None:
            CategoryTable.VM_CategoryTable = ViewModel_CategoryTable(vModel)
        # LinkSeparationLabelsToVMCategoryTable

        def LinkSeparationLabelsToVMCategoryTable(value_add_pair):
            if isinstance(value_add_pair.value, SeparationLable):
                row = self.GetRowOfValue(value_add_pair.value)
                if value_add_pair.bAdd:
                    self.InsertRow(row)
                    text = " " if self.bNoSeparationLabelText else "  " + value_add_pair.value.type.name.capitalize()
                    WF.MakeSeparationLabel(self, row, text)
                else:
                    self.UninsertRow(row)
        self.VM_CategoryTable._value_stream.subscribe(LinkSeparationLabelsToVMCategoryTable)

    def Refresh(self):
        super().Refresh()
        # Add Separation Labels
        for item in self.VM_CategoryTable:
            if isinstance(item, SeparationLable):
                text = " " if self.bNoSeparationLabelText else "  " + item.type.name.capitalize()
                WF.MakeSeparationLabel(self, self.GetRowOfValue(item), text)

    def AddSpacersForVMCategoryTable(self):
        row = self.iFirstDataRow
        # Determine height
        # fix: There must be a better way to determine the right height..
        height_widget = WF.MakeEntry_ReadOnly(self, (row, self.iFirstDataColumn), text="z", validation=BV.MakeValid_Money, display=BV.MakeValid_Money_ZeroIsNone)
        height_widget.update_idletasks()
        height = height_widget.winfo_height()
        height_widget.grid_forget()
        height_widget.destroy()
        # Data
        self.iSpacerColumn = self.iFirstDataColumn
        self.iFirstDataColumn += 1
        for item in self.VM_CategoryTable:
            if isinstance(item, BV.Model.Category):
                w = tk.Frame(self)
                w.grid(row=self.GetRowOfValue(item), column=self.iSpacerColumn)
                w.config(height=height)
        #

        def LinkSpacersToVMCategoryTable(value_add_pair):
            if isinstance(value_add_pair.value, BV.Model.Category):
                if value_add_pair.bAdd:
                    w = tk.Frame(self)
                    w.grid(row=self.GetRowOfValue(value_add_pair.value), column=self.iSpacerColumn)
                    w.config(height=height)
                else:
                    self.UninsertRow(self.GetRowOfValue(value_add_pair.value))
        self.cDisposables.append(self.VM_CategoryTable._value_stream.subscribe(LinkSpacersToVMCategoryTable))

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
            BVLog.warning(TM.FnName()+" could not find value:"+str(value)+" by name:"+("<NoName>" if not hasattr(value, 'name') else value.name)+" in VM_CategoryTable.")
            returning = None
        Log(TM.FnName()+". value:"+str(value)+" value_name:" + ("<NoName>" if not hasattr(value, 'name') else value.name)+" row:"+str(returning))
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

            def RemoveCategory(category):
                self.vModel.Categories.RemoveCategory(category)
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

            def RemoveCategory(category_name):  # fix: I should rx this
                print("Removing:"+category_name)
                self.vModel.Categories.RemoveCategory(category_name)

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
