import TM_CommonPy as TM  # noqa
import tkinter as tk
import rx
from .Skin import vSkin
import BudgetValue as BV


def MakeLable(self, cRowColumnPair, text=None, columnspan=1, width=0):
    if isinstance(width, BV.Buffer):
        width = len(text) + width.value
    w = tk.Label(self, font=vSkin.FONT_LARGE, borderwidth=2, width=width, height=1,
                 relief='ridge', background=vSkin.HEADER, text=text)
    w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan, sticky="ewn")


def MakeX(self, cRowColumnPair, command):
    w = tk.Button(self, text="X", font=vSkin.FONT_SMALL_BOLD, borderwidth=2, width=3, relief='ridge',
                  command=command)
    w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], sticky="ns")


def MakeHeader(self, cRowColumnPair, text=None, width=15, background=vSkin.HEADER):
    w = tk.Label(self, font=vSkin.FONT_SMALL_BOLD, borderwidth=2, width=width, height=1, relief='ridge',
                 background=background, text=text)
    w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], sticky="nsew")
    return w


def MakeRowHeader(*args, **kwargs):
    kwargs["bEditableState"] = False
    kwargs["justify"] = tk.LEFT
    kwargs["bBold"] = True
    return MakeEntry(*args, **kwargs)


def MakeEntry_ReadOnly(*args, **kwargs):
    kwargs["bEditableState"] = False
    return MakeEntry(*args, **kwargs)


def MakeEntry(self, cRowColumnPair, text=None, columnspan=1, bEditableState=True, justify=tk.RIGHT, bBold=False, background='SystemButtonFace'):
    text_ValueOrValueStream = text
    if bEditableState:
        state = "normal"
    else:
        state = "readonly"
    if bBold:
        font = vSkin.FONT_SMALL_BOLD
    else:
        font = vSkin.FONT_SMALL
    w = TM.tk.Entry(self, font=font, width=15, justify=justify,
                    borderwidth=2, relief='ridge', background=background, disabledbackground=background,
                    readonlybackground=background, state=state)
    # text
    if isinstance(text_ValueOrValueStream, rx.subjects.BehaviorSubject):
        def AssignText(w, value):
            try:
                w.text = value
            except tk.TclError:  # cell no longer exists
                pass
        w.AddDisposable(text_ValueOrValueStream.subscribe(lambda value, w=w: AssignText(w, value)))
    else:
        w.text = text_ValueOrValueStream
    #
    w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan, sticky="nsew")
    w.bind('<Escape>', lambda event: self.FocusNothing())
    if bEditableState:
        w.bind("<FocusIn>", lambda event, w=w: OnFocusIn_MakeObvious(w))
        w.bind("<FocusOut>", lambda event, w=w: w.MakeValid(), add="+")
        w.bind("<FocusOut>", lambda event, w=w: OnFocusOut_MakeObvious(w), add="+")
        w.bind("<Return>", lambda event, w=w: self.FocusNextWritableCell(w))
    return w


def MakeSeparationLable(parent, row, text):
    w = tk.Label(parent, font=vSkin.FONT_SMALL_BOLD, width=15, borderwidth=2, height=1, relief=tk.FLAT,
                 background='lightblue', text=text, anchor="w")
    w.grid(row=row, columnspan=1000, sticky="ew")  # columnspan?
    return w


def OnFocusIn_MakeObvious(cell):
    cell.config(justify=tk.LEFT)
    cell.select_text()


def OnFocusOut_MakeObvious(cell):
    cell.config(justify=tk.RIGHT)
