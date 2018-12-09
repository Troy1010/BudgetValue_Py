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

        for vItem in vModel.Categories.main_list:
            b = tk.Button(self, text=vItem,
                          command=lambda vItem=vItem, cell=cell, self=self: self.SelectCategory(vItem, cell))
            b.pack(fill=tk.BOTH, expand=True)

    def SelectCategory(self, category, cell):
        cursor = self.vModel.SpendingHistory.GetTable()
        cursor.execute(
            """ UPDATE 'SpendingHistory'
                SET Category = ?
                WHERE `index` = ?
                """,
            [category, cell.iRow]
        )
        self.vModel.connection.commit()
        cell.parent.Refresh()
        self.destroy()
