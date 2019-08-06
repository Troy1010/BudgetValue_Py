import TM_CommonPy as TM  # noqa
import tkinter as tk
from BudgetValue._Logger import Log  # noqa
from .Popup_Inheritable import Popup_Inheritable


class Popup_SelectCategory(Popup_Inheritable):
    previous_popup = None

    def __init__(self, parent, handler, cCategories, cPos=None, vDestroyHandler=None):
        super().__init__(parent, handler, cPos=cPos, vDestroyHandler=vDestroyHandler)
        # Show categories
        if cCategories is not None and len(cCategories):
            for category in cCategories:
                b = tk.Button(self, text=category.name,
                              command=lambda category=category: (self.handler(category), self.destroy()))
                b.pack(fill=tk.BOTH, expand=True)
        else:
            b = tk.Button(self, text="No Categories To Add", command=self.destroy)
            b.pack(fill=tk.BOTH, expand=True)
