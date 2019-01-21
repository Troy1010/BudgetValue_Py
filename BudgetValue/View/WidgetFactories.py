import TM_CommonPy as TM  # noqa
import tkinter as tk
from . import Fonts


def MakeHeader(self, cRowColumnPair, text=None):
    w = tk.Label(self, font=Fonts.FONT_SMALL_BOLD, borderwidth=2, width=15, height=1, relief='ridge',
                 background='SystemButtonFace', text=text)
    w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], sticky="ns")
    return w


def MakeEntry_ReadOnly(*args, **kwargs):
    kwargs["bEditableState"] = False
    return MakeEntry(*args, **kwargs)


def MakeEntry(self, cRowColumnPair, text=None, columnspan=1, bEditableState=True, justify=tk.RIGHT, bBold=False):
    if bEditableState:
        state = "normal"
        background = 'SystemButtonFace'
    else:
        state = "readonly"
        background = '#d8d8d8'
    if bBold:
        font = Fonts.FONT_SMALL_BOLD
    else:
        font = Fonts.FONT_SMALL
    w = TM.tk.Entry(self, font=font, width=15, justify=justify,
                    borderwidth=2, relief='ridge', background=background, disabledbackground=background,
                    readonlybackground=background, state=state)
    w.text = text
    w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan, sticky="ns")
    w.bind('<Escape>', lambda event: self.FocusNothing())
    if bEditableState:
        w.bind("<FocusIn>", lambda event, w=w: self.OnFocusIn_MakeObvious(w))
        w.bind("<FocusOut>", lambda event, w=w: self.OnFocusOut_MakeObvious(w), add="+")
        w.bind("<FocusOut>", lambda event, w=w: self.SaveCellToModel(w), add="+")
        w.bind("<Return>", lambda event, w=w: self.FocusNextWritableCell(w))
    return w


def MakeSeparationLable(parent, row, text):
    w = tk.Label(parent, font=Fonts.FONT_SMALL_BOLD, width=15, borderwidth=2, height=1, relief=tk.FLAT,
                 background='lightblue', text=text, anchor="w")
    w.grid(row=row, columnspan=1000, sticky="ew")  # columnspan?
    return w
