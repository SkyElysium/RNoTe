import sys

import tkinter as tk
from tkinter import messagebox

from core.config import *
from core.main_menu import MainMenu
from core.custom_notebook import CustomNotebook


class Editor(tk.Tk):
    def __init__(self) -> None:

        super().__init__()

        self.title(MAIN_WINDOW_TITLE)
        self.geometry(MAIN_WINDOW_SIZE)

        self.iconphoto(True, tk.PhotoImage(file = 'data/icon.png'))

        self.custom_notebook = CustomNotebook(self)
        self.custom_notebook.pack(fill = 'both', expand = True)

        self.main_menu = MainMenu(self)
        self.config(menu = self.main_menu)

        self.custom_notebook.add_tab()

        binding = {
            ('<Control-n>', '<Control-N>')         : self.custom_notebook.add_tab,
            ('<Control-o>', '<Control-O>')         : self.custom_notebook.open_file,
            ('<Control-s>', '<Control-S>')         : self.custom_notebook.save_file,
            ('<Control-Alt-s>', '<Control-Alt-S>') : self.custom_notebook.save_file_as,
            ('<Control-F4>',)                      : self.custom_notebook.safely_close_file,
            ('<Control-f>', '<Control-F>')         : self.main_menu.popup_find_dialog,
            ('<Control-plus>',)                    : self.main_menu.zoom_in_font,
            ('<Control-minus>',)                   : self.main_menu.zoom_out_font
        }

        for shortcuts, method in binding.items():
            for shortcut in shortcuts:
                self.bind(shortcut, method)

        self.protocol('WM_DELETE_WINDOW', self.exiting)

    def exiting(self) -> None:
        if_saved = []

        for tab_id in self.custom_notebook.tabs():
            path = self.custom_notebook.nametowidget(tab_id).path
            if path:
                self.main_menu.record_new_file(path)
            if_saved.append(self.custom_notebook.nametowidget(tab_id).text.edit_modified())

        if any(if_saved):
            reply = messagebox.askyesnocancel(
                title = MAIN_WINDOW_TITLE,
                message = '存在未保存的文件，在关闭程序前手动保存所有文件？'
            )
            if reply or reply is None:
                return

        sys.exit()
