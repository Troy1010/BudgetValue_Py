import TM_CommonPy as TM  # noqa
import tkinter as tk
from .Skin import vSkin
import rx
import BudgetValue as BV  # noqa
from datetime import datetime


class Buffer():
    def __init__(self, value):
        self.value = value - 1  # the -1 lets Buffer(0) do nothing as expected


def MakeLable(self, cRowColumnPair, text=None, columnspan=1, width=0, display=None, font=vSkin.FONT_LARGE):
    if isinstance(width, Buffer):
        width = len(text) + width.value
    #
    w = TM.tk.Label_DirectStream(self, font=font, borderwidth=2, width=width, height=1,
                                 relief='ridge', background=vSkin.BG_HEADER, text=text, display=display)
    w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan, sticky="ewn")
    return w


def MakeX(self, cRowColumnPair, command):
    w = tk.Button(self, text="X", font=vSkin.FONT_SMALL_BOLD, borderwidth=2, width=3, relief='ridge',
                  command=command)
    w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], sticky="ns")
    return w


def MakeHeader(self, cRowColumnPair, text=None, width=15, background=vSkin.BG_HEADER):
    if isinstance(width, Buffer):
        width = len(text) + width.value
    #
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
    if 'background' not in kwargs:
        kwargs["background"] = vSkin.BG_READ_ONLY
    return MakeEntry(*args, **kwargs)


def MakeButton(*args, pos=None, **kwargs):
    kwargs['relief'] = "groove"
    if 'width' not in kwargs:
        text = kwargs['text'] if not isinstance(kwargs['text'], rx.subjects.BehaviorSubject) else kwargs['text'].value
        if len(text)-1 < 10:
            kwargs['width'] = 10
    w = TM.tk.Button(*args, **kwargs)
    if pos:
        w.grid(row=pos[0], column=pos[1], columnspan=1000, sticky="nsew")
    else:
        w.pack(side=tk.LEFT, anchor='w')
    return w


def MakeEntry(self, cRowColumnPair, text=None, stream=None, columnspan=1, bEditableState=True, justify=tk.RIGHT, bBold=False, background=vSkin.BG_DEFAULT, width=0, bTextIsTimestamp=False, bFocusNothingOnReturn=False, validation=None, display=None):
    cDisposables = []
    if isinstance(width, Buffer):
        width = len(text) + width.value
    if isinstance(text, rx.subjects.BehaviorSubject) and isinstance(text.value, BV.Model.Category):
        temp_subject = rx.subjects.BehaviorSubject("")
        cDisposables.append(text.map(lambda category: category.name).subscribe(temp_subject))
        text = temp_subject
    if bTextIsTimestamp:
        temp_subject = rx.subjects.BehaviorSubject("")

        def MapTimestampToDatetimeString(timestamp):
            if timestamp == 0:
                return ""
            dt = datetime.fromtimestamp(timestamp)
            str_ = dt.strftime('%Y-%m-%d %H:%M')
            return str_
        obs = text.map(MapTimestampToDatetimeString)
        disposable = obs.subscribe(temp_subject)
        cDisposables.append(disposable)
        text = temp_subject
    #
    if isinstance(text, rx.Observable):  # FIX: unnecessary when usages are fixed.
        stream = text
        text = None
    #
    state = "normal" if bEditableState else "readonly"
    font = vSkin.FONT_SMALL_BOLD if bBold else vSkin.FONT_SMALL
    #
    w = TM.tk.Entry_DirectStream(self, font=font, width=width, justify=justify, text=text, stream=stream,
                                 borderwidth=2, relief='ridge', background=background, disabledbackground=background,
                                 readonlybackground=background, state=state, validation=validation, display=display)
    w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan, sticky="nsew")
    # Events
    w.bind('<Escape>', lambda event: w.FocusNothing())
    w.bind("<Return>", lambda event: w.FocusNothing())
    if bEditableState:
        w.bind("<FocusIn>", lambda event, w=w: OnFocusIn_MakeObvious(w))
        w.bind("<FocusOut>", lambda event, w=w: OnFocusOut_MakeObvious(w), add="+")
    # Remember disposables
    w.cDisposables.extend(cDisposables)
    #
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
