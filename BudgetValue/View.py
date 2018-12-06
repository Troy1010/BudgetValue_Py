import tkinter as tk
import tkinter.filedialog  # noqa
from tkinter import ttk as FancyTK
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
# Globals
LARGE_FONT = ("Verdana", 12)


class View(tk.Tk):
    def __init__(self, vModel, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="res/icon_coin_0MC_icon.ico")
        tk.Tk.wm_title(self, "Budget Value")

        cTabPages = (SpendingHistory, PaycheckPlan, NetWorth,
                     Spendables, Reports)
        # MenuBar
        vMenuBar = tk.Menu(self)
        self.config(menu=vMenuBar)
        vFileMenu = tk.Menu(vMenuBar, tearoff=False)
        vFileMenu.add_command(label="Import Spending History",
                              command=lambda vModel=vModel: SpendingHistory.ImportHistory(vModel))
        vMenuBar.add_cascade(label="File", menu=vFileMenu)
        vEditMenu = tk.Menu(vMenuBar, tearoff=False)
        vMenuBar.add_cascade(label="Edit", menu=vEditMenu)
        vSettingsMenu = tk.Menu(vMenuBar, tearoff=False)
        vSettingsMenu.add_command(label="Preferences..")
        vMenuBar.add_cascade(label="Settings", menu=vSettingsMenu)
        # TabBar
        vTabBar = TabBar(self, self, vModel, cTabPages)
        vTabBar.pack(side=tk.TOP, anchor='w', expand=False)
        # Tab Page Container
        vTabPageContainer = tk.Frame(self, borderwidth=2)
        vTabPageContainer.pack(side=tk.TOP, anchor='nw',
                               expand=True, fill="both")
        vTabPageContainer.grid_rowconfigure(0, weight=1)
        vTabPageContainer.grid_columnconfigure(0, weight=1)
        for F in cTabPages:
            frame = F(vTabPageContainer, self, vModel)
            vTabBar.cTabPageFrames[F] = frame
            frame.grid(row=0, sticky="nsew")

        vTabBar.ShowTab(SpendingHistory)


class TabBar(tk.Frame):
    cTabPageFrames = {}

    def __init__(self, parent, controller, vModel, cTabPages):
        tk.Frame.__init__(self, parent)

        self.cTabButtons = {}

        for i, vPage in enumerate(cTabPages):
            vButton = tk.Button(self, text=vPage.__name__, width=15,
                                command=lambda vPage=vPage: self.ShowTab(vPage))
            self.cTabButtons[vPage] = vButton
            vButton.grid(row=0, column=i)

    def ResetTabButtonColors(self):
        for vButton in self.cTabButtons.values():
            vButton.configure(background='grey')

    def ShowTab(self, controller):
        frame = self.cTabPageFrames[controller]
        # Highlight current tab
        self.ResetTabButtonColors()
        self.cTabButtons[controller].configure(background='SystemButtonFace')
        #
        frame.tkraise()


class SpendingHistory(tk.Frame):
    def __init__(self, parent, controller, vModel):
        tk.Frame.__init__(self, parent)
        # ImportHistory button
        vButton_ImportHistory = FancyTK.Button(self, text="Import Spending History",
                                               command=lambda vModel=vModel: SpendingHistory.ImportHistory(vModel))
        vButton_ImportHistory.pack(side=tk.TOP, anchor='w')
        # Table
        vTable = self.Table(self, controller, vModel)
        vTable.pack(side=tk.LEFT, anchor='w', expand=True, fill="both")
        # Scrollbar
        vScrollbar = tk.Scrollbar(self)
        vScrollbar.pack(side=tk.LEFT, anchor='w', fill="y")
        #
        vTable.config(yscrollcommand=vScrollbar.set)
        vScrollbar.config(command=vTable.yview)

    @staticmethod
    def ImportHistory(vModel):
        vFile = tk.filedialog.askopenfile()
        if vFile is not None:
            vModel.ImportHistory(vFile.name)

    class Table(tk.Canvas):
        def __init__(self, parent, controller, vModel):
            tk.Canvas.__init__(self, parent)
            vTableFrame = tk.Frame(self)
            self.create_window((0, 0), window=vTableFrame, anchor='nw')
            vTableFrame.bind("<Configure>", lambda event,
                             canvas=self: self.onFrameConfigure())
            cursor = vModel.connection.cursor()
            # Find cColWidths
            cursor.execute("SELECT * FROM 'transactions.csv'")
            cColWidths = {}
            for i, row in enumerate(cursor):
                for j, vItem in enumerate(row):
                    cColWidths[j] = min(
                        30, max(cColWidths.get(j, 0), len(str(vItem))))
            # Display table
            cursor.execute("SELECT * FROM 'transactions.csv'")
            for i, row in enumerate(cursor):
                if i > 15:
                    break
                for j, vItem in enumerate(row):
                    b = tk.Label(vTableFrame, text=str(vItem),
                                 borderwidth=2, width=cColWidths[j], relief='ridge', anchor='w')
                    b.grid(row=i, column=j)

        def onFrameConfigure(self):
            '''Reset the scroll region to encompass the inner frame'''
            self.configure(scrollregion=self.bbox("all"))


class PaycheckPlan(tk.Frame):
    def __init__(self, parent, controller, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Paycheck Plan", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()


class NetWorth(tk.Frame):
    def __init__(self, parent, controller, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Net Worth", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()


class Spendables(tk.Frame):
    def __init__(self, parent, controller, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Spendables", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()


class Reports(tk.Frame):
    def __init__(self, parent, controller, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Reports", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",
                                  command=lambda: controller.ShowTab(SpendingHistory))
        vButton1.pack()
