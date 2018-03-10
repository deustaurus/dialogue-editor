from tkinter import *
from Consts import ValidateResult

class PopupDialog(Toplevel):
    def __init__( self,  parent, title=None, label='Name:', inittext='', validate=None ):
        Toplevel.__init__(self, parent)
        self.transient(parent)
        self.validationfunc = validate
        
        self.validchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
        self.digitchars = '0123456789'

        if title:
            self.title(title)

        self.parent = parent

        self.result = None

        body = Frame(self)
        self.initial_focus = self.body(body, label, inittext)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.updateValidation('')

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    #
    # construction hooks

    def entrychanged(self, *args):
        self.updateValidation(self.sv.get())

    def body(self, master, label, init):
        Label(master, text=label).grid(row=0)

        self.sv = StringVar()
        self.sv.trace('w', self.entrychanged)
        vcmd = (self.register(self.inputvalidate),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'
        )
        self.e1 = Entry(master, validate='key', validatecommand=vcmd, width=50, textvariable=self.sv)
        self.e1.insert(END, init)
        self.e1.grid(row=0, column=1)

        Label(master, text='Status:').grid(row=1, column=0)
        self.detailsLabel = Label(master, text='')
        self.detailsLabel.grid(row=1, column=1, sticky=W)
        
        return self.e1 # initial focus

    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons

        box = Frame(self)

        self.okbutton = Button(box, text="OK", width=10, command=self.ok, state=DISABLED)
        self.okbutton.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics

    def ok(self, event=None):

        if self.validate(self.e1.get()) is not ValidateResult.SUCCESS:
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    #
    # command hooks
    def inputvalidate(
        self, 
        action, 
        index, 
        value_if_allowed, 
        prior_value, 
        text, 
        validaton_type, 
        trigger_type, 
        widget_name
    ):
        if text not in self.validchars:
            return False
        if int(index) == 0 and text in self.digitchars:
            return False
        return True
    
    def updateValidation(self, name):
        self.okbutton.config(state=DISABLED)        
        validresult = self.validate(name)
        if validresult == ValidateResult.LENGTH:
            self.detailsLabel.config(text='Enter Name')
        elif validresult == ValidateResult.NAME_CONFLICT:
            self.detailsLabel.config(text='Name Conflict')
        elif validresult == ValidateResult.RESERVED_NAME:
            self.detailsLabel.config(text='Reserved Name')
        else:
            self.okbutton.config(state=ACTIVE)
            self.detailsLabel.config(text='Valid Name')


    def validate(self, name):
        if self.validationfunc == None:
            return ValidateResult.SUCCESS
        return self.validationfunc(name)

    def apply(self):
        self.result = self.e1.get()
