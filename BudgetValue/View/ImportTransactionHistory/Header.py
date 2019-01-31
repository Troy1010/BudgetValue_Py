import tkinter as tk
import BudgetValue as BV
from BudgetValue.View.Skin import vSkin


class Header(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent

    def Refresh(self):
        # Remove old data
        for vWidget in BV.GetAllChildren(self):
            if 'tkinter.Text' in str(type(vWidget)):
                vWidget.grid_forget()
                vWidget.destroy()
        # Place new data
        for j, vItem in enumerate(self.vModel.ImportTransactionHistory.GetHeader()[1:]):
            b = tk.Text(self, font=vSkin.FONT_SMALL_BOLD,
                        borderwidth=2, width=self.parent.cColWidths[j], height=1, relief='ridge', background='SystemButtonFace')
            b.insert(1.0, str(vItem))
            b.grid(row=0, column=j)
            b.configure(state="disabled")
