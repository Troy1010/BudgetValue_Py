import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import rx  # noqa
from .Skin import vSkin  # noqa
import BudgetValue as BV  # noqa
from . import WidgetFactories as WF  # noqa
from Model.Misc import Dict_ValueStream


class RowToCategoryDict(Dict_ValueStream):

    def __init__(self, vModel):
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        #
        row = 2
        for category in self.vModel.Categories.Select():
            self[row] = category
            row += 2
        # If there is a new or removed category, update the dict

        def OnCategoryCreateOrDestroy(value_add_pair):
            pass
        self.vModel.Categories._value_stream.subscribe(OnCategoryCreateOrDestroy)
