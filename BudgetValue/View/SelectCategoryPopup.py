import TM_CommonPy as TM  # noqa
import tkinter as tk
from BudgetValue._Logger import Log  # noqa


class SelectCategoryPopup(tk.Frame):
    previous_popup = None

    def __init__(self, parent, vClosingHandler, cCategories, cPos, vDestroyHandler=None):
        # print("parent.winfo_toplevel():"+TM.Narrate(parent.winfo_toplevel()))
        parent = parent.winfo_toplevel()
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")
        self.destroy = TM.Hook(self.destroy, vDestroyHandler, bPrintAndQuitOnError=True)
        self.vClosingHandler = vClosingHandler
        # Delete old popup
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        self.__class__.previous_popup = self
        # Position myself
        x, y = cPos[0], cPos[1]
        self.place(in_=parent, x=x, y=y)
        self.tkraise()
        # Show categories
        if cCategories is not None and len(cCategories):
            for vCategory in cCategories:
                b = tk.Button(self, text=vCategory.name,
                              command=lambda vCategory=vCategory: self.SelectCategory(vCategory))
                b.pack(fill=tk.BOTH, expand=True)
        else:
            b = tk.Button(self, text="No Categories To Add", command=self.destroy)
            b.pack(fill=tk.BOTH, expand=True)
        # Bind Escape to exit
        self.winfo_toplevel().bind("<Escape>", lambda event: self.destroy())

    def SelectCategory(self, vCategory):
        self.vClosingHandler(vCategory)
        self.destroy()
