import tkinter as TK
import tkinter.filedialog  # noqa
from tkinter import ttk as FancyTK
import pickle
# Globals
LARGE_FONT = ("Verdana", 12)


class BudgetValueApp_Data():
    pass


class BudgetValueApp(TK.Tk):
    vBudgetValueApp_Data = BudgetValueApp_Data()

    def __init__(self, *args, **kwargs):
        TK.Tk.__init__(self, *args, **kwargs)
        TK.Tk.iconbitmap(self, default="res/icon_coin_0MC_icon.ico")
        TK.Tk.wm_title(self, "Budget Value")

        container = TK.Frame(self)

        cTabPages = (SpendingHistory, PaycheckPlan, NetWorth,
                     Spendables, Reports)
        self.cTabButtons = {}

        for i, vPage in enumerate(cTabPages):
            vButton = TK.Button(container, text=vPage.__name__,
                                command=lambda vPage=vPage: self.ShowTab(vPage))
            self.cTabButtons[vPage] = vButton
            vButton.grid(row=0, column=i, sticky="nsew")

        # fill to limits, expand beyond limits
        container.pack(side="top", fill="both", expand=True)
        # 0 is minimum, weight is sorta priority
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in cTabPages:
            frame = F(container, self)
            self.frames[F] = frame
            # NorthSouthEastWest alignment and stretch
            frame.grid(row=1, columnspan=len(cTabPages), sticky="nsew")

        self.ShowTab(SpendingHistory)

    def ResetTabButtonColors(self):
        for vButton in self.cTabButtons.values():
            vButton.configure(background='SystemButtonFace')

    def ShowTab(self, controller):
        frame = self.frames[controller]
        # Highlight current tab
        self.ResetTabButtonColors()
        self.cTabButtons[controller].configure(background='grey')
        #
        frame.tkraise()


def LoadHistory():
    vFile = TK.filedialog.askopenfile()
    print(vFile)


class SpendingHistory(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Spending History", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton_LoadHistory = FancyTK.Button(self, text="Upload History",
                                             command=lambda: LoadHistory())
        vButton_LoadHistory.pack()


class PaycheckPlan(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Paycheck Plan", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()


class NetWorth(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Net Worth", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()


class Spendables(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Spendables", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()


class Reports(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Reports", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()


app = BudgetValueApp()
app.mainloop()
