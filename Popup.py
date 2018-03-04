import tkSimpleDialog
from tkinter import *

class Popup(tkSimpleDialog.Dialog):

    def body(self, master):
        Label(master, text="Name:").grid(row=0)
        self.e1 = Entry(master)
        self.e1.grid(row=0, column=1)
        return self.e1 # initial focus

    def apply(self):
        self.result = self.e1.get()