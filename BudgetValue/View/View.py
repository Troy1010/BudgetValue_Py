from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import tkinter as tk
import tkinter.filedialog  # noqa
from tkinter import ttk
import BudgetValue as BV
from BudgetValue.View import Fonts
from BudgetValue.View.SpendFromCategories import SpendFromCategories
from BudgetValue.View.PaycheckPlan import PaycheckPlan
from BudgetValue.View.NetWorth import NetWorth
from BudgetValue.View.SplitMoneyIntoCategories import SplitMoneyIntoCategories


class View(tk.Tk):
    def __init__(self, vModel, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.iconbitmap(self, default="res/icon_coin_0MC_icon.ico")
        self.title("Budget Value")
        self.geometry('700x800')

        cTabPages = (SplitMoneyIntoCategories, SpendFromCategories, PaycheckPlan, NetWorth,
                     Reports)
        # MenuBar
        vMenuBar = MenuBar(vModel)
        self.config(menu=vMenuBar)
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

        vTabBar.ShowTab(cTabPages[1])


class MenuBar(tk.Menu):
    def __init__(self, vModel):
        tk.Menu.__init__(self)
        vFileMenu = tk.Menu(self, tearoff=False)
        vFileMenu.add_command(label="Import Spending History",
                              command=lambda vModel=vModel: BV.View.SpendFromCategories.ImportHistory(vModel))
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
        for i, page in enumerate(cTabPages):
            vButton = tk.Button(self, text=page.name, font=Fonts.FONT_MEDIUM,
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
        self.HighlightButton(self.cTabButtons[frame])
        self.cTabPageFrames[frame].tkraise()


class Reports(tk.Frame):
    name = "Reports"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        vLabel = ttk.Label(self, text="Reports",
                           font=Fonts.FONT_MEDIUM)
        vLabel.pack(pady=10, padx=10)

        vButton1 = ttk.Button(self, text="Spending History",)
        vButton1.pack()
