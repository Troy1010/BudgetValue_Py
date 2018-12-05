import tkinter as TK
from tkinter import ttk as FancyTK
import matplotlib
# Globals
LARGE_FONT = ("Verdana", 12)

matplotlib.use("TkAgg")


class BudgetValueApp(TK.Tk):
    def __init__(self, *args, **kwargs):
        TK.Tk.__init__(self, *args, **kwargs)
        TK.Tk.iconbitmap(self, default="res/icon_coin_0MC_icon.ico")

        container = TK.Frame(self)

        # fill to limits, expand beyond limits
        container.pack(side="top", fill="both", expand=True)
        # 0 is minimum, weight is sorta priority
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (SpendingHistory, PaycheckPlan, NetWorth, Spendables, Reports, TestFrame):
            frame = F(container, self)
            self.frames[F] = frame
            # NorthSouthEastWest alignment and stretch
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SpendingHistory)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()


class TestFrame(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Test Frame", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        #menubar = TK.Menu(controller)
        # self.config(menu=menubar)
        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.show_frame(SpendingHistory))
        vButton1.pack()


class SpendingHistory(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Spending History", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Paycheck Plan",
                                  command=lambda: controller.show_frame(PaycheckPlan))
        vButton1.pack()

        vButton1 = FancyTK.Button(self, text="NetWorth",
                                  command=lambda: controller.show_frame(NetWorth))
        vButton1.pack()

        vButton1 = FancyTK.Button(self, text="Spendables",
                                  command=lambda: controller.show_frame(Spendables))
        vButton1.pack()

        vButton1 = FancyTK.Button(self, text="Reports",
                                  command=lambda: controller.show_frame(Reports))
        vButton1.pack()

        vButton1 = FancyTK.Button(self, text="TestFrame",
                                  command=lambda: controller.show_frame(TestFrame))
        vButton1.pack()


class PaycheckPlan(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Paycheck Plan", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.show_frame(SpendingHistory))
        vButton1.pack()


class NetWorth(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Net Worth", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.show_frame(SpendingHistory))
        vButton1.pack()


class Spendables(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Spendables", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.show_frame(SpendingHistory))
        vButton1.pack()


class Reports(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Reports", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.show_frame(SpendingHistory))
        vButton1.pack()


app = BudgetValueApp()
app.mainloop()
