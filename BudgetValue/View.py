import tkinter as tk
import tkinter.filedialog  # noqa
from tkinter import ttk as FancyTK
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import BudgetValue as BV
# Globals
LARGE_FONT = ("Verdana", 12)
TEXT_FONT = ("Calibri", 10)


class View(tk.Tk):
    def __init__(self, vModel, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="res/icon_coin_0MC_icon.ico")
        #tk.Tk.wm_title(self, "Budget Value")
        self.title("Budget Value")
        self.geometry('700x800')

        cTabPages = (SpendingHistory, PaycheckPlan, NetWorth,
                     Spendables, Reports)
        # MenuBar
        vMenuBar = MenuBar(vModel)
        self.config(menu=vMenuBar)
        # TabBar
        vTabBar = TabBar(self, vModel, cTabPages)
        vTabBar.pack(side=tk.TOP, anchor='w', expand=False)
        # Tab Page Container
        vTabPageContainer = tk.Frame(self, borderwidth=2)
        vTabPageContainer.pack(side=tk.TOP, anchor='nw',
                               expand=True, fill="both")
        vTabPageContainer.grid_rowconfigure(0, weight=1)
        vTabPageContainer.grid_columnconfigure(0, weight=1)
        for vPage in cTabPages:
            frame = vPage(vTabPageContainer, vModel)
            vTabBar.cTabPageFrames[vPage] = frame
            frame.grid(row=0, sticky="nsew")

        vTabBar.ShowTab(SpendingHistory)


class MenuBar(tk.Menu):
    def __init__(self, vModel):
        tk.Menu.__init__(self)
        vFileMenu = tk.Menu(self, tearoff=False)
        vFileMenu.add_command(label="Import Spending History",
                              command=lambda vModel=vModel: SpendingHistory.ImportHistory(vModel))
        self.add_cascade(label="File", menu=vFileMenu)
        vEditMenu = tk.Menu(self, tearoff=False)
        self.add_cascade(label="Edit", menu=vEditMenu)
        vSettingsMenu = tk.Menu(self, tearoff=False)
        vSettingsMenu.add_command(label="Preferences..")
        self.add_cascade(label="Settings", menu=vSettingsMenu)


class TabBar(tk.Frame):
    cTabPageFrames = {}

    def __init__(self, parent, vModel, cTabPages):
        tk.Frame.__init__(self, parent)
        self.cTabButtons = {}
        for i, vFrame in enumerate(cTabPages):
            vButton = tk.Button(self, text=vFrame.__name__, width=15,
                                command=lambda vFrame=vFrame: self.ShowTab(vFrame))
            self.cTabButtons[vFrame] = vButton
            vButton.grid(row=0, column=i)

    def ResetTabButtonColors(self):
        for vButton in self.cTabButtons.values():
            vButton.configure(background='grey')

    def ShowTab(self, frame):
        frameObj = self.cTabPageFrames[frame]
        # Highlight current tab
        self.ResetTabButtonColors()
        self.cTabButtons[frame].configure(background='SystemButtonFace')
        #
        frameObj.tkraise()


class SpendingHistory(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        # ImportHistory button
        vButton_ImportHistory = FancyTK.Button(self, text="Import Spending History",
                                               command=lambda vModel=vModel: SpendingHistory.ImportHistory(vModel))
        vButton_ImportHistory.pack(side=tk.TOP, anchor='w')
        # TableFrame
        vTableFrame = tk.Frame(self)
        vTableFrame.pack(side=tk.LEFT, expand=True, fill="both")
        vTableFrame.grid_rowconfigure(0, weight=1)
        vTableFrame.grid_columnconfigure(0, weight=1)
        #  Table
        vTable = self.Table(vTableFrame, vModel)
        vTable.grid(row=0, column=0, sticky="NSEW")
        #  Scrollbars
        vScrollbar_Y = tk.Scrollbar(vTableFrame)
        vScrollbar_Y.grid(row=0, column=1, sticky="ns")
        vTable.config(yscrollcommand=vScrollbar_Y.set)
        vScrollbar_Y.config(command=vTable.yview)
        vScrollbar_X = tk.Scrollbar(vTableFrame, orient=tk.HORIZONTAL)
        vScrollbar_X.grid(row=1, column=0, sticky="ew")
        vTable.config(xscrollcommand=vScrollbar_X.set)
        vScrollbar_X.config(command=vTable.xview)

    @staticmethod
    def ImportHistory(vModel):
        vFile = tk.filedialog.askopenfile()
        if vFile is not None:
            vModel.ImportHistory(vFile.name)

    class Table(tk.Canvas):
        def __init__(self, parent, vModel):
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
                    cColWidths[j] = max(cColWidths.get(j, 0), len(str(vItem)))
                    if j < len(row) - 1:
                        cColWidths[j] = min(30, cColWidths[j])
            cursor.execute("SELECT * FROM 'transactions.csv'")
            names = [description[0] for description in cursor.description]
            for j, vItem in enumerate(names):
                cColWidths[j] = max(cColWidths.get(j, 0), len(str(vItem)))
                if j < len(row) - 1:
                    cColWidths[j] = min(30, cColWidths[j])
            # Display table
            #  Headers
            cursor.execute("SELECT * FROM 'transactions.csv'")
            #names = list(map(lambda x: x[0], cursor.description))
            names = [description[0] for description in cursor.description]
            for j, vItem in enumerate(names):
                b = tk.Text(vTableFrame, font=TEXT_FONT,
                            borderwidth=2, width=cColWidths[j], height=1, relief='ridge', background='SystemButtonFace')
                b.insert(1.0, vItem)
                b.grid(row=0, column=j)
                b.configure(state="disabled")

            #  Cells
            cursor.execute("SELECT * FROM 'transactions.csv'")
            for i, row in enumerate(cursor):
                for j, vItem in enumerate(row):
                    b = tk.Text(vTableFrame, font=TEXT_FONT,
                                borderwidth=2, width=cColWidths[j], height=1, relief='ridge', background='SystemButtonFace')
                    b.insert(1.0, str(vItem))
                    b.grid(row=i + 1, column=j)
                    b.configure(state="disabled")
            # Make table mousewheelable
            for vWidget in BV.GetAllChildren(self):
                vWidget.bind("<MouseWheel>", self.onMousewheel)

        def onFrameConfigure(self):
            '''Reset the scroll region to encompass the inner frame'''
            self.configure(scrollregion=self.bbox("all"))

        def onMousewheel(self, event):
            self.yview_scroll(int(-1 * (event.delta / 120)), "units")


class PaycheckPlan(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Paycheck Plan", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",)
        vButton1.pack()


class NetWorth(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Net Worth", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",)
        vButton1.pack()


class Spendables(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Spendables", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",)
        vButton1.pack()


class Reports(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Reports", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Spending History",)
        vButton1.pack()
