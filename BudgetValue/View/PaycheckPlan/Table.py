from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
import BudgetValue as BV
from BudgetValue.Model import CategoryType  # noqa
from BudgetValue.View import WidgetFactories as WF
from ...Model.Categories import Categories
from ..CategoryTable import CategoryTable
from ..Skin import vSkin


class Table(CategoryTable):
    def __init__(self, parent, vModel, *args, **kwargs):
        super().__init__(parent, vModel, *args, **kwargs)
        assert isinstance(vModel, BV.Model.Model)
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
        # Column Headers
        for j, header_name in enumerate(['Amount', 'Period', 'Plan']):
            w = WF.MakeHeader(self, (0, j+self.iFirstDataColumn), text=header_name)
            w.bPerminent = True
        # Link M -> V

        def LinkCategoryViewModelToView(col_edit_info):
            if not isinstance(col_edit_info.value, BV.Model.Category):
                return
            category = col_edit_info.value
            row = self.GetRowOfVMValue(category)
            assert row is not None
            if col_edit_info.bAdd:
                if category.IsSpendable():
                    WF.MakeEntry(self, (row, 1),
                                 text=self.vModel.PaycheckPlan[category.name].amount_over_period_stream,
                                 validation=BV.MakeValid_Money,
                                 display=BV.MakeValid_Money_ZeroIsNone)
                    WF.MakeEntry(self, (row, 2),
                                 text=self.vModel.PaycheckPlan[category.name].period_stream,
                                 validation=BV.MakeValid_Money,
                                 display=BV.MakeValid_Money_ZeroIsNone)
                    WF.MakeEntry(self, (row, 3),
                                 text=self.vModel.PaycheckPlan[category.name].amount_stream,
                                 validation=BV.MakeValid_Money,
                                 display=BV.MakeValid_Money_ZeroIsNone)
                else:
                    bEditableState = category != Categories.default_category
                    WF.MakeEntry(self, (row, 3),
                                 text=self.vModel.PaycheckPlan[category.name].amount_stream,
                                 bEditableState=bEditableState,
                                 background=vSkin.BG_READ_ONLY if not bEditableState else vSkin.BG_DEFAULT)
        self.VM_CategoryTable._value_stream.subscribe(LinkCategoryViewModelToView)
