import TM_CommonPy as TM  # noqa
import tkinter as tk
from tkinter import ttk
from BudgetValue._Logger import Log  # noqa
import BudgetValue as BV  # noqa
from .Popup_Inheritable import Popup_Inheritable


class Popup_SelectFromList(Popup_Inheritable):
    previous_popup = None

    def __init__(self, parent, handler, selection_list, cPos=None, vDestroyHandler=None):
        super().__init__(parent, handler, cPos=cPos, vDestroyHandler=vDestroyHandler)
        # Show combobox
        self.combobox_value = tk.StringVar()
        combo_box = ttk.Combobox(self)
        combo_box.config(textvariable=self.combobox_value, state="readonly")
        combo_box.config(values=selection_list, width=max([len(x) for x in selection_list]))
        combo_box.pack()

    def GetInputValue(self):
        return self.combobox_value.get() if self.combobox_value.get() != "" else None
