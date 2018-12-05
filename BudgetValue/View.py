import tkinter as tk
import tkinter.filedialog  # noqa
from tkinter import ttk as FancyTK
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import BudgetValue
# Globals
LARGE_FONT = ("Verdana", 12)
vModel = BudgetValue.BudgetValueModel()


class BudgetValueView(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="res/icon_coin_0MC_icon.ico")
        tk.Tk.wm_title(self, "Budget Value")

        cTabPages = (SpendingHistory, PaycheckPlan, NetWorth,
                     Spendables, Reports)
        self.cTabButtons = {}
        container = tk.Frame(self)
        for i, vPage in enumerate(cTabPages):
            vButton = tk.Button(container, text=vPage.__name__, width=15,
                                command=lambda vPage=vPage: self.ShowTab(vPage))
            self.cTabButtons[vPage] = vButton
            vButton.grid(row=0, column=i)

        container.pack(side="top", fill="both", expand=False)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in cTabPages:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=1, columnspan=len(cTabPages), sticky="nsew")

        self.ShowTab(SpendingHistory)

    def ResetTabButtonColors(self):
        for vButton in self.cTabButtons.values():
            vButton.configure(background='grey')

    def ShowTab(self, controller):
        frame = self.frames[controller]
        # Highlight current tab
        self.ResetTabButtonColors()
        self.cTabButtons[controller].configure(background='SystemButtonFace')
        #
        frame.tkraise()


class SpendingHistory(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        vButton1 = FancyTK.Button(
            self, text="Import Spendings History", command=self.ImportHistory)
        vButton1.grid(columnspan=5, sticky='W')

        for i in range(5):
            for j in range(5):
                b = tk.Entry(self, state="readonly")
                b.grid(row=i + 1, column=j)

    def ImportHistory(self):
        vFile = tk.filedialog.askopenfile()
        vModel.ImportHistory(vFile.name)


class PaycheckPlan(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Paycheck Plan", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()


class NetWorth(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Net Worth", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()


class Spendables(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Spendables", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()


class Reports(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Reports", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()
