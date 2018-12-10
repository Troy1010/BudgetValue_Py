import tkinter as tk
import BudgetValue as BV
from BudgetValue.View import Fonts


class Table(tk.Canvas):
    def __init__(self, parent, vModel):
        tk.Canvas.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
        # Assign TableWindow to Canvas
        self.vTableWindow = tk.Frame(self)
        self.create_window((0, 0), window=self.vTableWindow, anchor='nw')

    def Refresh(self):
        # Remove old data
        for vWidget in BV.GetAllChildren(self):
            if 'tkinter.Text' in str(type(vWidget)):
                vWidget.grid_forget()
                vWidget.destroy()
        # Place new data
        for i, row in enumerate(self.vModel.SpendingHistory.GetTable()):
            for j, vItem in enumerate(row[1:]):
                b = tk.Text(self.vTableWindow, font=Fonts.FONT_SMALL,
                            borderwidth=2, width=self.parent.cColWidths[j], height=1, relief='ridge', background='SystemButtonFace')
                b.insert(1.0, str(vItem))
                b.grid(row=i, column=j)
                b.configure(state="disabled")
                b.parent = self
                b.iRow = i
        self.update_idletasks()
        # Make scrollable
        self.vTableWindow.bind(
            "<Configure>", lambda event: self.onFrameConfigure())
        for vWidget in BV.GetAllChildren(self, bIncludeRoot=True):
            vWidget.bind("<MouseWheel>", self.onMousewheel)
        # Popup - Select Category
        for cell in self.vTableWindow.children.values():
            if cell.grid_info()['column'] == 0:
                cell.bind('<Button-1>', lambda event, cell=cell: BV.View.SpendingHistory.SelectCategoryPopup(cell, self.vModel))

    def onFrameConfigure(self):
        '''Reset the scroll region to encompass the inner frame'''
        self.configure(scrollregion=self.bbox("all"))

    def onMousewheel(self, event):
        self.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def Update(self, cRowColumnPair, value):
        self.vModel.SpendingHistory.Update(cRowColumnPair, value)
        if isinstance(cRowColumnPair[1], str):
            column = self.vModel.SpendingHistory.GetHeader()[1:].index(cRowColumnPair[1])  # View's table is missing the index column
        else:
            column = cRowColumnPair[1]
        cell = self.vTableWindow.grid_slaves(cRowColumnPair[0], column)[0]
        cell.config(state="normal")
        cell.delete("1.0", tk.END)
        cell.insert(1.0, value)
        cell.config(state="disabled")
