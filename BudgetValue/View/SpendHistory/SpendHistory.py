import tkinter as tk
from BudgetValue._Logger import BVLog  # noqa
import TM_CommonPy as TM  # noqa
from .Table import Table  # noqa
import BudgetValue as BV
from .. import WidgetFactories as WF
from ..BudgetedTable import BudgetedTable  # noqa
from ..Popup_InputAmount import Popup_InputAmount  # noqa


class SpendHistory(tk.Frame):
    name = "Spend From Categories"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        # ButtonBar
        self.vButtonBar = tk.Frame(self)
        self.vButtonBar.pack(side=tk.TOP, anchor='w')
        WF.MakeButton(self.vButtonBar, text="zoop")
        # Frame of tables
        self.vFrameOfTables = tk.Frame(self)
        self.vFrameOfTables.pack(side=tk.TOP, expand=True, fill="both")
        self.vFrameOfTables.grid_rowconfigure(1, weight=1)
        self.vFrameOfTables.grid_columnconfigure(0, weight=1)
        # BudgetedTable
        self.vBTCanvas = tk.Canvas(self.vFrameOfTables, highlightthickness=0)
        self.vBTCanvas.pack(side=tk.LEFT, fill='x', anchor='nw')
        self.vBTTable = BudgetedTable(self.vBTCanvas, vModel)
        self.vBTCanvas.create_window((0, 0), window=self.vBTTable, anchor='nw')
        self.vBTTable.pack(anchor='nw')
        self.vBTTable.Refresh()
        # Verticle Separator
        self.vVerticleSeparator = tk.Frame(self.vFrameOfTables, width=20)
        self.vVerticleSeparator.pack(side=tk.LEFT, anchor='nw', fill='both')
        # Scrollbar Frame
        self.vScrollbarFrame = tk.Frame(self.vFrameOfTables, background='lightgrey')
        self.vScrollbarFrame.grid_rowconfigure(1, weight=1)  # allows expansion
        self.vScrollbarFrame.grid_columnconfigure(0, weight=1)  # allows expansion
        self.vScrollbarFrame.pack(side=tk.LEFT, anchor='nw', fill='both', expand=True)
        # Table
        self.vCanvas = tk.Canvas(self.vScrollbarFrame, highlightthickness=0)
        self.vCanvas.grid(row=1, column=0, sticky="NSEW")
        self.vTable = Table(self.vCanvas, vModel)
        self.vCanvas.create_window((0, 0), window=self.vTable, anchor='nw')
        self.vTable.Refresh()
        # Column Headers
        self.vHeaderCanvas = tk.Canvas(self.vScrollbarFrame)
        self.vHeaderCanvas.grid(row=0, column=0, sticky="nsew")
        self.vHeaderFrame = tk.Frame(self.vHeaderCanvas, height=25)
        self.vHeaderFrame.grid_propagate(False)
        self.vHeaderFrame.grid(row=0, column=0, sticky="nw")
        # resize frame on data frame resize
        self.vTable.bind('<Configure>', lambda event: (
            self.vHeaderFrame.config(width=self.vTable.winfo_width())
        ))
        self.vTable.update_idletasks()
        self.vHeaderFrame.config(width=self.vTable.winfo_width())
        # resize canvas height on frame resize
        self.vHeaderFrame.bind('<Configure>', lambda event: (
            self.vHeaderCanvas.config(height=self.vHeaderFrame.winfo_height())
        ))
        # resize header canvas width on data canvas resize
        self.vTable.update_idletasks()
        self.vTable.bind('<Configure>', lambda event: (
            self.vHeaderCanvas.config(width=self.vTable.winfo_width()+500)
        ))
        self.vHeaderCanvas.config(width=self.vTable.winfo_width()+500)
        #
        self.vHeaderCanvas.create_window((0, 0), window=self.vHeaderFrame, anchor='nw')
        WF.MakeHeader(self.vHeaderFrame, (1, 0), text="Timestamp")
        w = tk.Frame(self.vHeaderFrame)
        w.grid(row=0, column=0, sticky='ew')
        self.LinkWidths(w, self.vTable.GetCell(0, 0))
        WF.MakeHeader(self.vHeaderFrame, (1, 1), text="Category")
        w = tk.Frame(self.vHeaderFrame)
        w.grid(row=0, column=1, sticky='ew')
        self.LinkWidths(w, self.vTable.GetCell(0, 1))
        WF.MakeHeader(self.vHeaderFrame, (1, 2), text="Amount")
        w = tk.Frame(self.vHeaderFrame)
        w.grid(row=0, column=2, sticky='ew')
        self.LinkWidths(w, self.vTable.GetCell(0, 2))
        WF.MakeHeader(self.vHeaderFrame, (1, 3), text="Description")
        w = tk.Frame(self.vHeaderFrame)
        w.grid(row=0, column=3, sticky='ew')
        self.LinkWidths(w, self.vTable.GetCell(0, 3))
        self.vHeaderCanvas.update_idletasks()
        self.vHeaderFrame.update_idletasks()
        self.vHeaderCanvas.update_idletasks()

        # Scrollbars
        vScrollbar_Y = tk.Scrollbar(self.vScrollbarFrame)
        vScrollbar_Y.grid(row=0, column=1, rowspan=2, sticky="ns")
        self.vCanvas.config(yscrollcommand=vScrollbar_Y.set)
        vScrollbar_Y.config(command=self.vCanvas.yview)
        vScrollbar_X = tk.Scrollbar(self.vScrollbarFrame, orient=tk.HORIZONTAL)
        vScrollbar_X.grid(row=2, column=0, sticky="ew")
        self.vCanvas.config(xscrollcommand=vScrollbar_X.set)
        #
        self.vTable.update_idletasks()
        self.vHeaderFrame.config(width=self.vTable.winfo_width())
        print("self.vTable:"+str(self.vTable.winfo_width()))
        print("self.vHeaderFrame:"+str(self.vHeaderFrame.winfo_width()))

        def ScrollHeaderAndData(*args):
            # print("ScrollHeaderAndData:"+str(args))
            self.vCanvas.xview(*args)
            self.vHeaderCanvas.xview(*args)
        vScrollbar_X.config(command=ScrollHeaderAndData)
        # Scroll Events
        self.vScrollbarFrame.bind('<Configure>', lambda event: self.vCanvas.config(scrollregion=self.vCanvas.bbox("all")), add='+')
        self.vScrollbarFrame.bind('<Configure>', lambda event: self.vHeaderCanvas.config(scrollregion=self.vHeaderCanvas.bbox("all")), add='+')

        def onMousewheel(event):
            self.vCanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.vScrollbarFrame.bind('<Enter>', lambda event: self.bind_all("<MouseWheel>", onMousewheel))
        self.vScrollbarFrame.bind('<Leave>', lambda event: self.unbind_all("<MouseWheel>"))
        # ButtonBar Buttons

        def AddSpend(amount):
            self.vModel.TransactionHistory.AddTransaction(amount=-amount, bSpend=True, description="nonverified spend")
            self.vTable.Refresh()
        WF.MakeButton(self.vButtonBar, text="Add Unverified Spend", command=lambda: AddSpend(0))
        WF.MakeButton(self.vButtonBar, text="Refresh", command=self.Refresh)
        WF.MakeButton(self.vButtonBar, text="Update", command=lambda: self.Update_())
        WF.MakeButton(self.vButtonBar, text="Try YView", command=lambda: self.try_yview())
        WF.MakeButton(self.vButtonBar, text="Print bbox", command=lambda: self.PrintBBox())
        WF.MakeButton(self.vButtonBar, text="Clear!", command=lambda: (self.vModel.TransactionHistory.ClearAllTransactions(), self.Refresh()))

    def LinkWidths(self, widget1, widget2):
        if widget2 is None:  # fix
            return
        assert isinstance(widget1, tk.Frame)
        assert isinstance(widget2, tk.Frame)
        widget1.update_idletasks()  # makes winfo_width give correct results
        widget2.update_idletasks()  # makes winfo_width give correct results

        def forward_width_change(widget_from, widget_to):
            if widget_from.winfo_width() > widget_to.winfo_width():
                widget_to["width"] = widget_from.winfo_width()
        widget1.bind("<Configure>", lambda event, widget_from=widget1, widget_to=widget2: forward_width_change(widget_from, widget_to))
        widget2.bind("<Configure>", lambda event, widget_from=widget2, widget_to=widget1: forward_width_change(widget_from, widget_to))
        forward_width_change(widget1, widget2)
        forward_width_change(widget2, widget1)

    def PrintBBox(self):
        print("table bbox('all'):"+str(self.vTable.bbox("all")))
        print("canvas bbox('all'):"+str(self.vCanvas.bbox("all")))

    def Update_(self):
        self.update()

    def try_yview(self):
        self.vCanvas.yview("moveto", 0.1)

    def Refresh(self):
        self.vBTTable.Refresh()
        self.vTable.Refresh()
