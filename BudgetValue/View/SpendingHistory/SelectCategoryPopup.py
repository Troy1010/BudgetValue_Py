import TM_CommonPy as TM  # noqa
import tkinter as tk


class SelectCategoryPopup(tk.Frame):
    previous_popup = None

    def __init__(self, parent, cell, vModel):
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")
        self.vModel = vModel
        # Delete old popup
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        self.__class__.previous_popup = self

        for vCategory in vModel.Categories.main_list:
            b = tk.Button(self, text=vCategory.name,
                          command=lambda vCategory=vCategory, cell=cell, self=self: self.SelectCategory(vCategory, cell))
            b.pack(fill=tk.BOTH, expand=True)

    def SelectCategory(self, vCategory, cell):
        self.vModel.SpendingHistory.Update(
            (cell.iRow, "Category"), vCategory.name)
        cell.parent.Refresh()
        self.destroy()
