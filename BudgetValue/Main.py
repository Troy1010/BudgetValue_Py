import tkinter as TK
from tkinter import ttk as FancyTK

LARGE_FONT = ("Verdana", 12)


class BudgetValueApp(TK.Tk):
    def __init__(self, *args, **kwargs):
        TK.Tk.__init__(self, *args, **kwargs)
        TK.Tk.iconbitmap(self, default="res/icon_coin_0MC_icon.ico")

        container = TK.Frame(self)

        # fill to limits, expand beyond limits
        container.pack(side="top", fill="both", expand=True)
        # 0 is minimum, weight is sorta priority
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo):
            frame = F(container, self)
            self.frames[F] = frame
            # NorthSouthEastWest alignment and stretch
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()


class StartPage(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Start Page", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Page 1",
                                  command=lambda: controller.show_frame(PageOne))
        vButton1.pack()
        vButton2 = FancyTK.Button(self, text="Page 2",
                                  command=lambda: controller.show_frame(PageTwo))
        vButton2.pack()


class PageOne(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Page 1", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Home",
                                  command=lambda: controller.show_frame(StartPage))
        vButton1.pack()
        vButton2 = FancyTK.Button(self, text="Page 2",
                                  command=lambda: controller.show_frame(PageTwo))
        vButton2.pack()


class PageTwo(TK.Frame):
    def __init__(self, parent, controller):
        TK.Frame.__init__(self, parent)
        vLabel = FancyTK.Label(self, text="Page 2", font=LARGE_FONT)
        vLabel.pack(pady=10, padx=10)

        vButton1 = FancyTK.Button(self, text="Home",
                                  command=lambda: controller.show_frame(StartPage))
        vButton1.pack()
        vButton2 = FancyTK.Button(self, text="Page 1",
                                  command=lambda: controller.show_frame(PageOne))
        vButton2.pack()


app = BudgetValueApp()
app.mainloop()
