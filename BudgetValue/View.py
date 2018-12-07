import tkinter as tk
import tkinter.filedialog  # noqa
from tkinter import ttk
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import BudgetValue as BV
import itertools
# Globals
FONT_LARGE = ("Verdana", 12)
FONT_TEXT = ("Calibri", 10)
FONT_TEXT_BOLD = ("Calibri", 10, "bold")


class View(tk.Tk):
    def __init__(self, vModel, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.iconbitmap(self, default="res/icon_coin_0MC_icon.ico")
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

    def HighlightButton(self, vButtonToHighlight):
        for vButton in self.cTabButtons.values():
            color = 'SystemButtonFace' if vButton == vButtonToHighlight else 'grey'
            vButton.configure(background=color)

    def ShowTab(self, frame):
        self.HighlightButton(self.cTabButtons[frame])
        self.cTabPageFrames[frame].tkraise()


class SpendingHistory(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        # ButtonBar
        vButtonFrame = tk.Frame(self)
        vButtonFrame.pack(side=tk.TOP, anchor='w')
        # TableFrame
        vTableFrame = tk.Frame(self, background='lightgrey')
        vTableFrame.pack(side=tk.TOP, expand=True, fill="both")
        vTableFrame.grid_rowconfigure(1, weight=1)
        vTableFrame.grid_columnconfigure(0, weight=1)
        vTableFrame.cColWidths = self.GetColWidths(vModel)
        #  Header
        vHeader = self.Header(vTableFrame, vModel)
        vHeader.grid(row=0, column=0, sticky="NSEW")
        #  Table
        self.vTable = self.Table(vTableFrame, vModel)
        self.vTable.grid(row=1, column=0, sticky="NSEW")
        #  Scrollbars
        vScrollbar_Y = tk.Scrollbar(vTableFrame)
        vScrollbar_Y.grid(row=0, rowspan=2, column=1, sticky="ns")
        self.vTable.config(yscrollcommand=vScrollbar_Y.set)
        vScrollbar_Y.config(command=self.vTable.yview)
        vScrollbar_X = tk.Scrollbar(vTableFrame, orient=tk.HORIZONTAL)
        vScrollbar_X.grid(row=2, column=0, sticky="ew")
        self.vTable.config(xscrollcommand=vScrollbar_X.set)
        vScrollbar_X.config(command=self.vTable.xview)
        # ButtonBar - continued
        vButton_ImportHistory = ttk.Button(vButtonFrame, text="Import Spending History",
                                           command=lambda self=self: self.ImportHistory())
        vButton_ImportHistory.pack(side=tk.LEFT, anchor='w')
        vButton_Refresh = ttk.Button(vButtonFrame, text="Refresh",
                                     command=lambda self=self: self.Table.Refresh(self.vTable))
        vButton_Refresh.pack(side=tk.LEFT, anchor='w')

    def ImportHistory(self):
        # Prompt which file
        vFile = tk.filedialog.askopenfile()
        # Import
        if vFile is not None:
            self.vModel.SpendingHistory.Import(vFile.name)
        # Refresh view
        self.vTable.Refresh()

    def GetColWidths(self, vModel):
        cColWidths = {}
        for row in itertools.chain([vModel.SpendingHistory.GetHeader()], vModel.SpendingHistory.GetTable()):
            for j, vItem in enumerate(row):
                cColWidths[j] = max(cColWidths.get(j, 0), len(str(vItem)) + 1)
                if j < len(row) - 1:
                    cColWidths[j] = min(30, cColWidths[j])
        return cColWidths

    class Header(tk.Frame):
        def __init__(self, parent, vModel):
            tk.Frame.__init__(self, parent)
            for j, vItem in enumerate(vModel.SpendingHistory.GetHeader()):
                b = tk.Text(self, font=FONT_TEXT_BOLD,
                            borderwidth=2, width=parent.cColWidths[j], height=1, relief='ridge', background='SystemButtonFace')
                b.insert(1.0, str(vItem))
                b.grid(row=0, column=j)
                b.configure(state="disabled")

    class Table(tk.Canvas):
        def __init__(self, parent, vModel):
            tk.Canvas.__init__(self, parent)
            self.vModel = vModel
            self.parent = parent
            # Assign TableWindow to Canvas
            self.vTableWindow = tk.Frame(self)
            self.create_window((0, 0), window=self.vTableWindow, anchor='nw')
            # Table
            self.Refresh()

        def Refresh(self):
            # Remove old data
            for vWidget in BV.GetAllChildren(self):
                if 'tkinter.Text' in str(type(vWidget)):
                    vWidget.grid_forget()
                    vWidget.destroy()
            # Place new data
            for i, row in enumerate(self.vModel.SpendingHistory.GetTable()):
                for j, vItem in enumerate(row):
                    b = tk.Text(self.vTableWindow, font=FONT_TEXT,
                                borderwidth=2, width=self.parent.cColWidths[j], height=1, relief='ridge', background='SystemButtonFace')
                    b.insert(1.0, str(vItem))
                    b.grid(row=i, column=j)
                    b.configure(state="disabled")
            self.update_idletasks()
            # Make scrollable
            self.vTableWindow.bind("<Configure>", lambda event,
                                   canvas=self: self.onFrameConfigure())
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
        vLabel = ttk.Label(self, text="Paycheck Plan", font=FONT_LARGE)
        vLabel.pack(pady=10, padx=10)

        vButton1 = ttk.Button(self, text="Spending History",)
        vButton1.pack()


class NetWorth(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = ttk.Label(self, text="Net Worth", font=FONT_LARGE)
        vLabel.pack(pady=10, padx=10)

        vButton1 = ttk.Button(self, text="Spending History",)
        vButton1.pack()


class Spendables(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = ttk.Label(self, text="Spendables", font=FONT_LARGE)
        vLabel.pack(pady=10, padx=10)

        vButton1 = ttk.Button(self, text="Spending History",)
        vButton1.pack()


class Reports(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = ttk.Label(self, text="Reports", font=FONT_LARGE)
        vLabel.pack(pady=10, padx=10)

        vButton1 = ttk.Button(self, text="Spending History",)
        vButton1.pack()
