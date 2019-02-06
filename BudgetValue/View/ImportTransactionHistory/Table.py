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
        for i, row in enumerate(self.vModel.ImportTransactionHistory.GetTable()):
            for j, vItem in enumerate(row[1:]):
                w = tk.Text(self.vTableWindow, font=vSkin.FONT_SMALL,
                            borderwidth=2, width=self.parent.cColWidths[j], height=1, relief='ridge', background='SystemButtonFace')
                w.insert(1.0, str(vItem))
                w.grid(row=i, column=j)
                w.configure(state="disabled")
                w.parent = self
                w.iRow = i
                if j == 0:  # category row
                    w.bind('<Button-1>', lambda event, w=w, x=w.winfo_width(), y=0: (
                        BV.View.Popup_SelectCategory(self.winfo_toplevel(),
                                                     lambda category, w=w: self.SelectCategory(category, w),
                                                     self.vModel.Categories.values(),
                                                     vDestroyHandler=lambda w=w: self.DestroyHandler(w)
                                                     ),
                        w.config(background="grey")
                    ))
        #
        self.update_idletasks()
        # Make scrollable
        self.vTableWindow.bind("<Configure>", lambda event: self.onFrameConfigure())
        for vWidget in BV.GetAllChildren(self, bIncludeRoot=True):
            vWidget.bind("<MouseWheel>", self.onMousewheel)

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
        self.vModel.ImportTransactionHistory.Update(row, columnName, value)
        if isinstance(columnName, str):
            iColumn = self.vModel.ImportTransactionHistory.GetHeader()[1:].index(columnName)  # View's table is missing the index column
        cell = self.vTableWindow.grid_slaves(row, iColumn)[0]
        cell.config(state="normal")
        cell.delete("1.0", tk.END)
        cell.insert(1.0, value)
        cell.config(state="disabled")
