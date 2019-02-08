from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import tkinter as tk
import tkinter.filedialog  # noqa
from tkinter import ttk
import BudgetValue as BV
from BudgetValue.View.Skin import vSkin
from BudgetValue.View.ImportTransactionHistory import ImportTransactionHistory
from BudgetValue.View.PaycheckPlan import PaycheckPlan
from BudgetValue.View.Accounts import Accounts
from BudgetValue.View.SplitMoneyIntoCategories import SplitMoneyIntoCategories
from BudgetValue.View.SpendHistory import SpendHistory
from BudgetValue.View.VerifyTransactions import VerifyTransactions  # noqa
import os
import pickle


class View(tk.Tk):
    def __init__(self, vModel, *args, **kwargs):
        assert(isinstance(vModel, BV.Model.Model))
        tk.Tk.__init__(self, *args, **kwargs)
        self.vModel = vModel
        self.destroy = TM.Hook(self.destroy, self.Save, bPrintAndQuitOnError=True)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.iconbitmap(self, default="res/icon_coin_0MC_icon.ico")
        self.title("Budget Value")
        self.geometry('900x800')
        self.sSaveFile = os.path.join(vModel.sWorkspace, "View.pickle")
        self.vLastShownTab = SplitMoneyIntoCategories
        self.Load()

        cTabPages = (SplitMoneyIntoCategories, SpendHistory, Accounts, Reports, PaycheckPlan, ImportTransactionHistory)
        # MenuBar
        self.config(menu=MenuBar(vModel))
        # TabBar
        vTabBar = TabBar(self, vModel, cTabPages)
        vTabBar.pack(side=tk.TOP, anchor='w', expand=False)
        # TabPageContainer
        vTabPageContainer = tk.Frame(self, borderwidth=2)
        vTabPageContainer.pack(side=tk.TOP, anchor='nw', expand=True, fill="both")
        vTabPageContainer.grid_rowconfigure(0, weight=1)
        vTabPageContainer.grid_columnconfigure(0, weight=1)
        for vPage in cTabPages:
            frame = vPage(vTabPageContainer, vModel)
            vTabBar.cTabPageFrames[vPage] = frame
            frame.grid(row=0, sticky="nsew")

        vTabBar.ShowTab(self.vLastShownTab)

    def Save(self):
        self.vModel.TransactionHistory.Save()
        #
        data = [self.vLastShownTab]
        with open(self.sSaveFile, 'wb') as f:
            pickle.dump(data, f)

    def Load(self):
        if not os.path.exists(self.sSaveFile):
            return
        with open(self.sSaveFile, 'rb') as f:
            data = None
            try:
                data = pickle.load(f)
            except ModuleNotFoundError:  # module has been renamed
                pass
        if data is None:
            return
        self.vLastShownTab = data[0]


class MenuBar(tk.Menu):
    def __init__(self, vModel):
        tk.Menu.__init__(self)
        vFileMenu = tk.Menu(self, tearoff=False)
        vFileMenu.add_command(label="Import Spend History",
                              command=lambda vModel=vModel: BV.View.ImportTransactionHistory.ImportHistory(vModel))
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
        self.parent = parent
        for i, page in enumerate(cTabPages):
            vButton = tk.Button(self, text=page.name, font=vSkin.FONT_MEDIUM,
                                command=lambda page=page: self.ShowTab(page))
            self.cTabButtons[page] = vButton
            # Make width at least 15
            if len(vButton['text']) < 15:
                vButton.configure(width=max(vButton.winfo_width(), 15))
            #
            vButton.grid(row=0, column=i)

    def HighlightButton(self, vButtonToHighlight):
        for vButton in self.cTabButtons.values():
            color = 'SystemButtonFace' if vButton == vButtonToHighlight else 'grey'
            vButton.configure(background=color)

    def ShowTab(self, frame):
        if frame not in self.cTabButtons:
            frame = list(self.cTabButtons.keys())[0]
        self.HighlightButton(self.cTabButtons[frame])
        self.cTabPageFrames[frame].tkraise()
        self.parent.vLastShownTab = frame


class Reports(tk.Frame):
    name = "Reports"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = ttk.Label(self, text="Reports",
                           font=vSkin.FONT_MEDIUM)
        vLabel.pack(pady=10, padx=10)
