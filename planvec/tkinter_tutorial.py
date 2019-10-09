import tkinter as tk


WINDOW_SIZE = '400x300'


class Window(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        # changing the title of our master widget
        self.master.title("GUI")

        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)

        # creating a button instance
        quitButton = tk.Button(self, text="Quit")

        # placing the button on my window
        quitButton.place(x=0, y=0)


def main():
    root = tk.Tk()
    root.geometry(WINDOW_SIZE)
    app = Window(root)
    root.mainloop()


if __name__ == '__main__':
    main()
