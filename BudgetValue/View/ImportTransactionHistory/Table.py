import tkinter as tk
import BudgetValue as BV
from BudgetValue.View.Skin import vSkin


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
                b = tk.Text(self.vTableWindow, font=vSkin.FONT_SMALL,
                            borderwidth=2, width=self.parent.cColWidths[j], height=1, relief='ridge', background='SystemButtonFace')
                b.insert(1.0, str(vItem))
                b.grid(row=i, column=j)
                b.configure(state="disabled")
                b.parent = self
                b.iRow = i
        self.update_idletasks()
        # Make scrollable
        self.vTableWindow.bind("<Configure>", lambda event: self.onFrameConfigure())
        for vWidget in BV.GetAllChildren(self, bIncludeRoot=True):
            vWidget.bind("<MouseWheel>", self.onMousewheel)
        # Popup - Select Category
        for cell in self.vTableWindow.children.values():
            if cell.grid_info()['column'] == 0:
                cell.bind('<Button-1>', lambda event, cell=cell, x=cell.winfo_width(), y=0: (
                          cell.config(background="grey"),
                          BV.View.SelectCategoryPopup(self.parent, self.SelectCategory, self.vModel.Categories.values(), (x, y), cell, vDestroyHandler=self.DestroyHandler)))

    def DestroyHandler(self, cell):
        try:
            cell.config(background="SystemButtonFace")
        except tk.TclError:  # cell doesn't exist
            pass

    def SelectCategory(self, vCategory, cell):
        self.Update(cell.grid_info()['row'], "Category", vCategory.name)

    def onFrameConfigure(self):
        '''Reset the scroll region to encompass the inner frame'''
        self.configure(scrollregion=self.bbox("all"))

    def onMousewheel(self, event):
        self.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def Update(self, row, columnName, value):
        self.vModel.SpendingHistory.Update(row, columnName, value)
        if isinstance(columnName, str):
            iColumn = self.vModel.SpendingHistory.GetHeader()[1:].index(columnName)  # View's table is missing the index column
        cell = self.vTableWindow.grid_slaves(row, iColumn)[0]
        cell.config(state="normal")
        cell.delete("1.0", tk.END)
        cell.insert(1.0, value)
        cell.config(state="disabled")
