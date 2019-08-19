import TM_CommonPy as TM  # noqa
import tkinter as tk
import rx
from . import WidgetFactories as WF  # noqa
import time
from datetime import datetime


class Popup_SelectDate(tk.Frame):
    previous_popup = None

    def __init__(self, parent, timestamp_handler, old_timestamp, cPos=None, vDestroyHandler=None):
        tk.Frame.__init__(self, parent, borderwidth=2, background="black")

        def ForgetPrevPopup():
            self.__class__.previous_popup = None
        self.destroy = TM.Hook(self.destroy, vDestroyHandler, ForgetPrevPopup, bPrintAndQuitOnError=True)
        # Delete old popup
        if self.__class__.previous_popup is not None:
            self.__class__.previous_popup.destroy()
        self.__class__.previous_popup = self
        # Position myself
        if not cPos:
            x, y = parent.winfo_pointerx() - parent.winfo_rootx(), parent.winfo_pointery() - parent.winfo_rooty()
        else:
            x, y = cPos[0], cPos[1]
        self.place(x=x, y=y)
        self.tkraise()
        # Define validations

        def ValidateYear(x):
            return TM.WithinRange(int(x), 1970, 3000)

        def ValidateMonth(x):
            return TM.WithinRange(int(x), 1, 12)

        def ValidateDay(x, year, month):
            if month == 1:
                max_ = 31
            elif month == 2:
                max_ = 28
                if year % 4 == 0:  # leap year
                    max_ += 1
            elif month == 3:
                max_ = 31
            elif month == 4:
                max_ = 30
            elif month == 5:
                max_ = 31
            elif month == 6:
                max_ = 30
            elif month == 7:
                max_ = 31
            elif month == 8:
                max_ = 31
            elif month == 9:
                max_ = 30
            elif month == 10:
                max_ = 31
            elif month == 11:
                max_ = 30
            elif month == 12:
                max_ = 31
            return TM.WithinRange(int(x), 1, max_)

        def ValidateHour(x):
            return TM.WithinRange(int(x), 1, 12)

        def ValidateMinute(x):
            return TM.WithinRange(int(x), 0, 59)
        # Show date chart
        dt = datetime.fromtimestamp(old_timestamp)
        year = rx.subjects.BehaviorSubject(dt.year)
        month = rx.subjects.BehaviorSubject(dt.month)
        day = rx.subjects.BehaviorSubject(dt.day)
        rx.Observable.combine_latest(  # days validation rely on year and month
            year, month,
            lambda year, month: ValidateDay(day.value, year, month)
        ).subscribe(day)
        hour = rx.subjects.BehaviorSubject(dt.hour)
        minute = rx.subjects.BehaviorSubject(dt.minute)
        self.MakeEntry((0, 0), year, validation=ValidateYear)
        self.MakeEntry((1, 0), month, validation=ValidateMonth)
        self.MakeEntry((2, 0), day, validation=lambda x, month_stream=month, year_stream=year: ValidateDay(x, year_stream.value, month_stream.value))
        self.MakeEntry((3, 0), hour, validation=ValidateHour)
        self.MakeEntry((4, 0), minute, validation=ValidateMinute)
        self.timestamp = rx.subjects.BehaviorSubject(0)
        rx.Observable.combine_latest(
            year, month, day, hour, minute,
            lambda *cArgs: time.mktime(datetime(*cArgs).timetuple())
        ).subscribe(self.timestamp)
        # trigger subscription
        self.timestamp.subscribe()
        year.on_next(year.value)
        # Bind Return to accept

        def OnReturn(event):
            if isinstance(event.widget, tk.Entry):
                return
            timestamp_handler(self.timestamp.value)
            self.destroy()
        self.winfo_toplevel().bind("<Return>", OnReturn, add='+')
        # OK button
        WF.MakeX(self, (5, 0), lambda: (timestamp_handler(self.timestamp.value), self.destroy()))
        # Bind Escape to exit
        self.winfo_toplevel().bind("<Escape>", lambda event: self.destroy(), add='+')

    def MakeEntry(self, cRowColumnPair, text, validation=None):
        return WF.MakeEntry(self, cRowColumnPair, text=text, validation=validation, bFocusNothingOnReturn=True)
