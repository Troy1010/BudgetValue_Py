import tkinter as tk
from tkinter import ttk
import tkinter.filedialog  # noqa
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
import tkinter.messagebox  # noqa
from .Table import Table
import BudgetValue as BV
import rx
from .. import WidgetFactories as WF
from ..Skin import vSkin
from ...Model.Categories import Categories
from ..Popup_SelectIncome import Popup_SelectIncome


class SplitMoneyIntoCategories(tk.Frame):
    name = "Split Money Into Categories"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        vButton_SplitTransactionPaycheck = ttk.Button(self.vButtonBar, text="Split Paycheck from Transactions",
                                                      command=lambda self=self: self.SplitTransactionPaycheck())
        vButton_SplitTransactionPaycheck.pack(side=tk.LEFT, anchor='w')
        vButton_SplitUnverifiedPaycheck = ttk.Button(self.vButtonBar, text="Split unverified Paycheck",
                                                     command=lambda self=self: self.SplitUnverifiedPaycheck())
        vButton_SplitUnverifiedPaycheck.pack(side=tk.LEFT, anchor='w')
        vButton_AddRow = ttk.Button(self.vButtonBar, text="Add 500, Split",
                                    command=lambda self=self: self.Split500())
        vButton_AddRow.pack(side=tk.LEFT, anchor='w')
        # Button_SplitDifference
        vSplitDifferenceText_stream = rx.subjects.BehaviorSubject("")
        self.vModel.Balance.balance_stream.map(
            lambda balance: "Split Difference (" + str(balance) + ")"
        ).subscribe(vSplitDifferenceText_stream)
        vButton_SplitDifference = WF.MakeButton(self.vButtonBar, text=vSplitDifferenceText_stream,
                                                command=lambda self=self: self.SplitDifference())

        def HighlightBalanceButton(balance):
            if balance:
                vButton_SplitDifference.config(background=vSkin.BG_BAD)
            else:
                vButton_SplitDifference.config(background=vSkin.BG_DEFAULT)
        self.vModel.Balance.balance_stream.subscribe(HighlightBalanceButton)
        # Button_SplitAccounts
        vButton_SplitAccounts = ttk.Button(self.vButtonBar, text="Split Accounts",
                                           command=lambda self=self: self.buttonPressed.on_next(None))
        vButton_SplitAccounts.pack(side=tk.LEFT, anchor='w')
        self.buttonPressed = rx.subjects.Subject()
        self.buttonPressed.with_latest_from(
            self.vModel.Accounts.total_stream,
            lambda pressEvent, total: total
        ).subscribe(lambda x: self.SplitAccounts(x))
        # Table
        self.vCanvas = tk.Canvas(self, highlightthickness=0)
        self.vCanvas.pack(side=tk.TOP, fill='x', anchor='nw')
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        self.vTable.pack(anchor='nw')
        self.vTable.Refresh()
        # ButtonBar More
        vButton_Refresh = ttk.Button(self.vButtonBar, text="Refresh",
                                     command=lambda self=self: self.vTable.Refresh())
        vButton_Refresh.pack(side=tk.LEFT, anchor='w')

    def SplitTransaction(self, transaction):
        pass

    def SplitTransactionPaycheck(self):
        Popup_SelectIncome(self, self.SplitTransaction)

    def SplitUnverifiedPaycheck(self):
        pass

    def SplitDifference(self):
        self.vModel.SplitMoneyHistory.AddColumn()
        self.vModel.SplitMoneyHistory.AddEntry(-1, Categories.default_income, amount=self.vModel.Balance.balance_stream.value)
        self.vTable.Refresh()

    def SplitPaycheck(self):
        self.vModel.SplitMoneyHistory.AddColumn()
        for categoryName, paycheckPlan_row in self.vModel.PaycheckPlan.items():
            if categoryName == Categories.default_category.name:
                continue
            self.vModel.SplitMoneyHistory.AddEntry(-1, categoryName, amount=paycheckPlan_row.amount)
        self.vTable.Refresh()

    def SplitAccounts(self, amount):
        self.vModel.SplitMoneyHistory.AddColumn()
        self.vModel.SplitMoneyHistory.AddEntry(-1, Categories.default_income, amount=amount)
        self.vTable.Refresh()

    def AddSplitMoneyHistoryColumn(self):
        self.vModel.SplitMoneyHistory.AddColumn()
        self.vTable.Refresh()

    def Split500(self):
        self.vModel.TransactionHistory.AddTransaction(amount=500)
        self.vTable.Refresh()
