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
            for j, vItem in enumerate(row):
                b = tk.Text(self.vTableWindow, font=Fonts.FONT_SMALL,
                            borderwidth=2, width=self.parent.cColWidths[j], height=1, relief='ridge', background='SystemButtonFace')
                b.insert(1.0, str(vItem))
                b.grid(row=i, column=j)
                b.configure(state="disabled")
                b.parent = self
        self.update_idletasks()
        # Make scrollable
        self.vTableWindow.bind(
            "<Configure>", lambda event: self.onFrameConfigure())
        for vWidget in BV.GetAllChildren(self, bIncludeRoot=True):
            vWidget.bind("<MouseWheel>", self.onMousewheel)
        # Popup - Select Catagory
        for cell in self.vTableWindow.children.values():
            if cell.grid_info()['column'] == 0:
                cell.bind(
                    '<Button-1>', lambda event, cell=cell: self.OpenSelectCatagoryPopup(cell))

    def onFrameConfigure(self):
        '''Reset the scroll region to encompass the inner frame'''
        self.configure(scrollregion=self.bbox("all"))

    def onMousewheel(self, event):
        self.yview_scroll(int(-1 * (event.delta / 120)), "units")

    oldCell = None

    def HighlightCell(self, cell):
        if self.oldCell is not None:
            self.oldCell.config(background="SystemButtonFace")
        self.oldCell = cell
        cell.config(background="grey")

    def OpenSelectCatagoryPopup(self, cell):
        self.HighlightCell(cell)
        vPopup = BV.View.SpendingHistory.SelectCatagoryPopup.Root(
            cell.parent, self.vModel)
        vPopup.place(x=0
                     + cell.winfo_width(), y=0)
        vPopup.tkraise()
