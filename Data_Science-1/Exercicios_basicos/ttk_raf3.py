from tkinter import messagebox

"""
Yes/No Questions¶
The tkinter messagebox object also allows you to ask a user simple yes/no
type questions and varies the button names based on the type of question.
These functions are:
"""

answer = messagebox.askokcancel("Question","Do you want to open this file?")
answer = messagebox.askretrycancel("Question", "Do you want to try that again?")
answer = messagebox.askyesno("Question","Do you like Python?")
answer = messagebox.askyesnocancel("Question", "Continue playing?")
