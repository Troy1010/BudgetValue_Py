import TM_CommonPy as TM  # noqa
import tkinter as tk
from BudgetValue._Logger import Log  # noqa


class Popup_SelectCategory(tk.Frame):
    previous_popup = None

    def __init__(self, parent, category_handler, cCategories, cPos=None, vDestroyHandler=None):
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")
        # Hook destroy handlers

        def ForgetPrevPopup():
            self.__class__.previous_popup = None
        self.destroy = TM.Hook(self.destroy, vDestroyHandler, ForgetPrevPopup, bPrintAndQuitOnError=True)
        # Delete old popup
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        self.__class__.previous_popup = self
        # Position myself
        if not cPos:
            x, y = parent.winfo_pointerx() - parent.winfo_rootx(), parent.winfo_pointery() - parent.winfo_rooty()
        else:
            x, y = cPos[0], cPos[1]
        self.place(x=x, y=y)
        self.tkraise()
        # Show categories
        if cCategories is not None and len(cCategories):
            for category in cCategories:
                b = tk.Button(self, text=category.name,
                              command=lambda category=category: (category_handler(category), self.destroy()))
                b.pack(fill=tk.BOTH, expand=True)
        else:
            b = tk.Button(self, text="No Categories To Add", command=self.destroy)
            b.pack(fill=tk.BOTH, expand=True)
        # Bind Escape to exit
        self.winfo_toplevel().bind("<Escape>", lambda event: self.destroy(), add='+')
